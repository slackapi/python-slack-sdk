"""aiohttp based Socket Mode client

* https://api.slack.com/apis/connections/socket
* https://slack.dev/python-slack-sdk/socket-mode/
* https://pypi.org/project/aiohttp/

"""
import asyncio
import logging
import time
from asyncio import Future, Lock
from asyncio import Queue
from logging import Logger
from typing import Union, Optional, List, Callable, Awaitable

import aiohttp
from aiohttp import ClientWebSocketResponse, WSMessage, WSMsgType, ClientConnectionError

from slack_sdk.proxy_env_variable_loader import load_http_proxy_from_env
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
    trace_enabled: bool

    last_ping_pong_time: Optional[float]
    current_session: Optional[ClientWebSocketResponse]
    current_session_monitor: Optional[Future]

    auto_reconnect_enabled: bool
    default_auto_reconnect_enabled: bool
    closed: bool
    stale: bool
    connect_operation_lock: Lock

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
        ping_interval: float = 5,
        trace_enabled: bool = False,
        on_message_listeners: Optional[List[Callable[[WSMessage], None]]] = None,
        on_error_listeners: Optional[List[Callable[[WSMessage], None]]] = None,
        on_close_listeners: Optional[List[Callable[[WSMessage], None]]] = None,
    ):
        """Socket Mode client

        Args:
            app_token: App-level token
            logger: Custom logger
            web_client: Web API client
            auto_reconnect_enabled: True if automatic reconnection is enabled (default: True)
            ping_interval: interval for ping-pong with Slack servers (seconds)
            trace_enabled: True if more verbose logs to see what's happening under the hood
            proxy: the HTTP proxy URL
            on_message_listeners: listener functions for on_message
            on_error_listeners: listener functions for on_error
            on_close_listeners: listener functions for on_close
        """
        self.app_token = app_token
        self.logger = logger or logging.getLogger(__name__)
        self.web_client = web_client or AsyncWebClient()
        self.closed = False
        self.stale = False
        self.connect_operation_lock = Lock()
        self.proxy = proxy
        if self.proxy is None or len(self.proxy.strip()) == 0:
            env_variable = load_http_proxy_from_env(self.logger)
            if env_variable is not None:
                self.proxy = env_variable

        self.default_auto_reconnect_enabled = auto_reconnect_enabled
        self.auto_reconnect_enabled = self.default_auto_reconnect_enabled
        self.ping_interval = ping_interval
        self.trace_enabled = trace_enabled
        self.last_ping_pong_time = None

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
        try:
            while not self.closed:
                try:
                    await asyncio.sleep(self.ping_interval)
                    if self.current_session is not None:
                        t = time.time()
                        if self.last_ping_pong_time is None:
                            self.last_ping_pong_time = float(t)
                        await self.current_session.ping(f"sdk-ping-pong:{t}")

                    if self.auto_reconnect_enabled:
                        should_reconnect = False
                        if self.current_session is None or self.current_session.closed:
                            self.logger.info(
                                "The session seems to be already closed. Reconnecting..."
                            )
                            should_reconnect = True

                        if self.last_ping_pong_time is not None:
                            disconnected_seconds = int(
                                time.time() - self.last_ping_pong_time
                            )
                            if disconnected_seconds >= (self.ping_interval * 4):
                                self.logger.info(
                                    "The connection seems to be stale. Reconnecting..."
                                    f" reason: disconnected for {disconnected_seconds}+ seconds)"
                                )
                                self.stale = True
                                self.last_ping_pong_time = None
                                should_reconnect = True

                        if should_reconnect is True or not await self.is_connected():
                            await self.connect_to_new_endpoint()

                except Exception as e:
                    self.logger.error(
                        "Failed to check the current session or reconnect to the server "
                        f"(error: {type(e).__name__}, message: {e})"
                    )
        except asyncio.CancelledError:
            if self.trace_enabled:
                self.logger.debug(
                    "The running monitor_current_session task is now cancelled"
                )
            raise

    async def receive_messages(self) -> None:
        try:
            consecutive_error_count = 0
            while not self.closed:
                try:
                    message: WSMessage = await self.current_session.receive()
                    if self.trace_enabled and self.logger.level <= logging.DEBUG:
                        type = WSMsgType(message.type)
                        message_type = type.name if type is not None else message.type
                        message_data = message.data
                        if isinstance(message_data, bytes):
                            message_data = message_data.decode("utf-8")
                        if len(message_data) > 0:
                            # To skip the empty message that Slack server-side often sends
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
                                    "Received CLOSE event. Reconnecting..."
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
                        elif message.type == WSMsgType.PING:
                            await self.current_session.pong(message.data)
                            continue
                        elif message.type == WSMsgType.PONG:
                            if message.data is not None:
                                str_message_data = message.data.decode("utf-8")
                                elements = str_message_data.split(":")
                                if (
                                    len(elements) == 2
                                    and elements[0] == "sdk-ping-pong"
                                ):
                                    try:
                                        self.last_ping_pong_time = float(elements[1])
                                    except Exception as e:
                                        self.logger.warning(
                                            f"Failed to parse the last_ping_pong_time value from {str_message_data}"
                                            f" - error : {e}"
                                        )
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
        except asyncio.CancelledError:
            if self.trace_enabled:
                self.logger.debug("The running receive_messages task is now cancelled")
            raise

    async def is_connected(self) -> bool:
        return (
            not self.closed
            and not self.stale
            and self.current_session is not None
            and not self.current_session.closed
        )

    async def connect(self):
        old_session = None if self.current_session is None else self.current_session
        if self.wss_uri is None:
            self.wss_uri = await self.issue_new_wss_url()
        self.current_session = await self.aiohttp_client_session.ws_connect(
            self.wss_uri,
            autoping=False,
            heartbeat=self.ping_interval,
            proxy=self.proxy,
        )
        self.auto_reconnect_enabled = self.default_auto_reconnect_enabled
        self.stale = False
        self.logger.info("A new session has been established")

        if self.current_session_monitor is not None:
            self.current_session_monitor.cancel()

        self.current_session_monitor = asyncio.ensure_future(
            self.monitor_current_session()
        )

        if self.message_receiver is not None:
            self.message_receiver.cancel()

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
        try:
            await self.current_session.send_str(message)
        except ConnectionError as e:
            # We rarely get this exception while replacing the underlying WebSocket connections.
            # We can do one more try here as the self.current_session should be ready now.
            if self.logger.level <= logging.DEBUG:
                self.logger.debug(
                    f"Failed to send a message (error: {e}, message: {message})"
                    " as the underlying connection was replaced. Retrying the same request only one time..."
                )
            # Although acquiring self.connect_operation_lock also for the first method call is the safest way,
            # we avoid synchronizing a lot for better performance. That's why we are doing a retry here.
            try:
                await self.connect_operation_lock.acquire()
                if await self.is_connected():
                    await self.current_session.send_str(message)
                else:
                    self.logger.warning(
                        "The current session is no longer active. Failed to send a message"
                    )
                    raise e
            finally:
                if self.connect_operation_lock.locked() is True:
                    self.connect_operation_lock.release()

    async def close(self):
        self.closed = True
        self.auto_reconnect_enabled = False
        await self.disconnect()
        if self.message_processor is not None:
            self.message_processor.cancel()
        if self.current_session_monitor is not None:
            self.current_session_monitor.cancel()
        if self.message_receiver is not None:
            self.message_receiver.cancel()
        if self.aiohttp_client_session is not None:
            await self.aiohttp_client_session.close()
