import asyncio
import logging
from asyncio import Future
from asyncio import Queue
from logging import Logger
from typing import Union, Optional, List, Callable, Awaitable

import aiohttp
from aiohttp import ClientWebSocketResponse, WSMessage, WSMsgType, ClientConnectionError

from slack_sdk.socket_mode.async_client import AsyncBaseSocketModeClient
from slack_sdk.socket_mode.async_listeners import (
    AsyncWebSocketMessageListener,
    AsyncSocketModeRequestListener,
)
from slack_sdk.socket_mode.request import SocketModeRequest
from slack_sdk.web.async_client import AsyncWebClient


class SocketModeClient(AsyncBaseSocketModeClient):
    logger: Logger
    web_client: AsyncWebClient
    app_token: str
    wss_uri: Optional[str]
    auto_reconnect_enabled: bool
    message_queue: Queue
    message_listeners: List[
        Union[
            AsyncWebSocketMessageListener,
            Callable[
                ["AsyncBaseSocketModeClient", dict, Optional[str]], Awaitable[None]
            ],
        ]
    ]
    socket_mode_request_listeners: List[
        Union[
            AsyncSocketModeRequestListener,
            Callable[["AsyncBaseSocketModeClient", SocketModeRequest], Awaitable[None]],
        ]
    ]

    message_receiver: Optional[Future]
    message_processor: Future

    proxy: Optional[str]
    ping_interval: float
    current_session: Optional[ClientWebSocketResponse]
    current_session_monitor: Optional[Future]

    auto_reconnect_enabled: bool
    default_auto_reconnect_enabled: bool
    closed: bool

    on_message_listeners: List[Callable[[WSMessage], Awaitable[None]]]
    on_error_listeners: List[Callable[[WSMessage], Awaitable[None]]]
    on_close_listeners: List[Callable[[WSMessage], Awaitable[None]]]

    def __init__(
        self,
        app_token: str,
        logger: Optional[Logger] = None,
        web_client: Optional[AsyncWebClient] = None,
        proxy: Optional[str] = None,
        auto_reconnect_enabled: bool = True,
        ping_interval: float = 10,
        on_message_listeners: Optional[List[Callable[[WSMessage], None]]] = None,
        on_error_listeners: Optional[List[Callable[[WSMessage], None]]] = None,
        on_close_listeners: Optional[List[Callable[[WSMessage], None]]] = None,
    ):
        self.app_token = app_token
        self.logger = logger or logging.getLogger(__name__)
        self.web_client = web_client or AsyncWebClient()
        self.closed = False
        self.proxy = proxy
        self.default_auto_reconnect_enabled = auto_reconnect_enabled
        self.auto_reconnect_enabled = self.default_auto_reconnect_enabled
        self.ping_interval = ping_interval

        self.wss_uri = None
        self.message_queue = Queue()
        self.message_listeners = []
        self.socket_mode_request_listeners = []
        self.current_session = None
        self.current_session_monitor = None

        # https://docs.aiohttp.org/en/stable/client_reference.html
        # Unless you are connecting to a large, unknown number of different servers
        # over the lifetime of your application,
        # it is suggested you use a single session for the lifetime of your application
        # to benefit from connection pooling.
        self.aiohttp_client_session = aiohttp.ClientSession()

        self.on_message_listeners = on_message_listeners or []
        self.on_error_listeners = on_error_listeners or []
        self.on_close_listeners = on_close_listeners or []

        self.message_receiver = None
        self.message_processor = asyncio.ensure_future(self.process_messages())

    async def monitor_current_session(self) -> None:
        while not self.closed:
            await asyncio.sleep(self.ping_interval)
            try:
                if self.auto_reconnect_enabled and (
                    self.current_session is None or self.current_session.closed
                ):
                    self.logger.info(
                        "The session seems to be already closed. Going to reconnect..."
                    )
                    await self.connect_to_new_endpoint()
            except Exception as e:
                self.logger.error(
                    "Failed to check the current session or reconnect to the server "
                    f"(error: {type(e).__name__}, message: {e})"
                )

    async def receive_messages(self) -> None:
        consecutive_error_count = 0
        while not self.closed:
            try:
                message: WSMessage = await self.current_session.receive()
                if self.logger.level <= logging.DEBUG:
                    type = WSMsgType(message.type)
                    message_type = type.name if type is not None else message.type
                    message_data = message.data
                    if isinstance(message_data, bytes):
                        message_data = message_data.decode("utf-8")
                    self.logger.debug(
                        f"Received message (type: {message_type}, data: {message_data}, extra: {message.extra})"
                    )
                if message is not None:
                    if message.type == WSMsgType.TEXT:
                        message_data = message.data
                        await self.enqueue_message(message_data)
                        for listener in self.on_message_listeners:
                            await listener(message)
                    elif message.type == WSMsgType.CLOSE:
                        if self.auto_reconnect_enabled:
                            self.logger.info(
                                "Received CLOSE event. Going to reconnect..."
                            )
                            await self.connect_to_new_endpoint()
                        for listener in self.on_close_listeners:
                            await listener(message)
                    elif message.type == WSMsgType.ERROR:
                        for listener in self.on_error_listeners:
                            await listener(message)
                    elif message.type == WSMsgType.CLOSED:
                        await asyncio.sleep(self.ping_interval)
                        continue
                consecutive_error_count = 0
            except Exception as e:
                consecutive_error_count += 1
                self.logger.error(
                    f"Failed to receive or enqueue a message: {type(e).__name__}, {e}"
                )
                if isinstance(e, ClientConnectionError):
                    await asyncio.sleep(self.ping_interval)
                else:
                    await asyncio.sleep(consecutive_error_count)

    async def connect(self):
        old_session = None if self.current_session is None else self.current_session
        if self.wss_uri is None:
            self.wss_uri = await self.issue_new_wss_url()
        self.current_session = await self.aiohttp_client_session.ws_connect(
            self.wss_uri,
            heartbeat=self.ping_interval,
            proxy=self.proxy,
        )
        self.auto_reconnect_enabled = self.default_auto_reconnect_enabled
        self.logger.info("A new session has been established")

        if self.current_session_monitor is None:
            self.current_session_monitor = asyncio.ensure_future(
                self.monitor_current_session()
            )

        if self.message_receiver is None:
            self.message_receiver = asyncio.ensure_future(self.receive_messages())

        if old_session is not None:
            await old_session.close()
            self.logger.info("The old session has been abandoned")

    async def disconnect(self):
        if self.current_session is not None:
            await self.current_session.close()
        self.logger.info("The session has been abandoned")

    async def send_message(self, message: str):
        if self.logger.level <= logging.DEBUG:
            self.logger.debug(f"Sending a message: {message}")
        await self.current_session.send_str(message)

    async def close(self):
        self.closed = True
        self.auto_reconnect_enabled = False
        await self.disconnect()
        self.message_processor.cancel()
        if self.current_session_monitor is not None:
            self.current_session_monitor.cancel()
        if self.message_receiver is not None:
            self.message_receiver.cancel()
        if self.aiohttp_client_session is not None:
            await self.aiohttp_client_session.close()
