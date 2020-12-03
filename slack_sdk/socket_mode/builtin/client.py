import logging
import time
from concurrent.futures.thread import ThreadPoolExecutor
from logging import Logger
from queue import Queue
from threading import Lock
from typing import Union, Optional, List, Callable

from .connection import Connection
from slack_sdk.socket_mode.client import BaseSocketModeClient
from slack_sdk.socket_mode.listeners import (
    WebSocketMessageListener,
    SocketModeRequestListener,
)
from slack_sdk.socket_mode.request import SocketModeRequest
from slack_sdk.web import WebClient


class SocketModeClient(BaseSocketModeClient):
    logger: Logger
    web_client: WebClient
    app_token: str
    wss_uri: Optional[str]
    message_queue: Queue
    message_listeners: List[
        Union[
            WebSocketMessageListener,
            Callable[["BaseSocketModeClient", dict, Optional[str]], None],
        ]
    ]
    socket_mode_request_listeners: List[
        Union[
            SocketModeRequestListener,
            Callable[["BaseSocketModeClient", SocketModeRequest], None],
        ]
    ]

    current_app_executor: ThreadPoolExecutor
    current_app_monitor: ThreadPoolExecutor
    current_app_monitor_started: bool

    message_processor: ThreadPoolExecutor
    message_workers: ThreadPoolExecutor

    current_session: Optional[Connection]

    auto_reconnect_enabled: bool
    default_auto_reconnect_enabled: bool
    trace_enabled: bool

    connect_operation_lock: Lock

    on_message_listeners: List[Callable[[str], None]]
    on_error_listeners: List[Callable[[Exception], None]]
    on_close_listeners: List[Callable[[int, Optional[str]], None]]

    def __init__(
        self,
        app_token: str,
        logger: Optional[Logger] = None,
        web_client: Optional[WebClient] = None,
        auto_reconnect_enabled: bool = True,
        trace_enabled: bool = False,
        ping_interval: float = 10,
        concurrency: int = 10,
        proxy: Optional[str] = None,
        on_message_listeners: Optional[List[Callable[[str], None]]] = None,
        on_error_listeners: Optional[List[Callable[[Exception], None]]] = None,
        on_close_listeners: Optional[List[Callable[[int, Optional[str]], None]]] = None,
    ):
        self.app_token = app_token
        self.logger = logger or logging.getLogger(__name__)
        self.web_client = web_client or WebClient()
        self.default_auto_reconnect_enabled = auto_reconnect_enabled
        self.auto_reconnect_enabled = self.default_auto_reconnect_enabled
        self.trace_enabled = trace_enabled
        self.ping_interval = ping_interval
        self.wss_uri = self.issue_new_wss_url()
        self.message_queue = Queue()
        self.message_listeners = []
        self.socket_mode_request_listeners = []

        self.current_session = None
        self.current_app_monitor = ThreadPoolExecutor(1)
        self.current_app_monitor_started = False
        self.current_app_executor = ThreadPoolExecutor(1)

        self.connect_operation_lock = Lock()

        self.message_processor = ThreadPoolExecutor(1)
        self.message_processor.submit(self.process_messages)
        self.message_workers = ThreadPoolExecutor(max_workers=concurrency)

        self.proxy = proxy

        self.on_message_listeners = on_message_listeners or []
        self.on_error_listeners = on_error_listeners or []
        self.on_close_listeners = on_close_listeners or []

    def session_id(self) -> Optional[str]:
        if self.current_session is not None:
            return self.current_session.session_id
        return None

    def is_connected(self) -> bool:
        return self.current_session is not None \
               and self.current_session.is_active()

    def connect(self) -> None:
        def on_message(message: str):
            if self.logger.level <= logging.DEBUG:
                self.logger.debug(f"on_message invoked: (message: {message})")
            self.enqueue_message(message)
            for listener in self.on_message_listeners:
                listener(message)

        def on_error(error: Exception):
            self.logger.error(
                f"on_error invoked (session id: {self.session_id()}, "
                f"error: {type(error).__name__}, message: {error})",
                error,
            )
            for listener in self.on_error_listeners:
                listener(error)

        def on_close(code: int, reason: Optional[str] = None):
            if self.logger.level <= logging.DEBUG:
                self.logger.debug(f"on_close invoked (session id: {self.session_id()})")
            if self.auto_reconnect_enabled:
                self.logger.info(
                    "Received CLOSE event. Going to reconnect... "
                    f"(session id: {self.session_id()})"
                )
                self.connect_to_new_endpoint()
            for listener in self.on_close_listeners:
                listener(code, reason)

        old_session: Optional[Connection] = self.current_session
        self.current_session = Connection(
            url=self.wss_uri,
            logger=self.logger,
            ping_interval=self.ping_interval,
            trace_enabled=self.trace_enabled,
            proxy=self.proxy,
            on_message_listener=on_message,
            on_error_listener=on_error,
            on_close_listener=on_close,
        )
        self.current_session.connect()
        self.auto_reconnect_enabled = self.default_auto_reconnect_enabled

        def run_current_session():
            self.current_session.run_forever()

        def monitor_current_session():
            while True:
                time.sleep(self.ping_interval)
                try:
                    if self.auto_reconnect_enabled and (
                        self.current_session is None
                        or not self.current_session.is_active()
                    ):
                        self.logger.info(
                            "The session seems to be already closed. Going to reconnect... "
                            f"(session id: {self.session_id()})"
                        )
                        self.connect_to_new_endpoint()
                except Exception as e:
                    self.logger.error(
                        "Failed to check the current session or reconnect to the server "
                        f"(session id: {self.session_id()}, error: {type(e).__name__}, message: {e})"
                    )

        self.current_app_executor.submit(run_current_session)
        if not self.current_app_monitor_started:
            self.current_app_monitor.submit(monitor_current_session)
            self.current_app_monitor_started = True

        self.logger.info(
            f"A new session has been established (session id: {self.session_id()})"
        )
        if old_session is not None:
            old_session.close()

    def disconnect(self) -> None:
        self.current_session.close()
        self.auto_reconnect_enabled = False

    def send_message(self, message: str) -> None:
        if self.logger.level <= logging.DEBUG:
            self.logger.debug(
                f"Sending a message (session id: {self.session_id()}, message: {message})"
            )
        self.current_session.send(message)

    def close(self):
        self.disconnect()
        self.current_app_monitor.shutdown()
        self.current_app_executor.shutdown()
        self.message_processor.shutdown()
        self.message_workers.shutdown()
