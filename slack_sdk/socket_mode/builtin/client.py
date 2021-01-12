import logging
from concurrent.futures.thread import ThreadPoolExecutor
from logging import Logger
from queue import Queue
from threading import Lock
from typing import Union, Optional, List, Callable

from slack_sdk.socket_mode.client import BaseSocketModeClient
from slack_sdk.socket_mode.listeners import (
    WebSocketMessageListener,
    SocketModeRequestListener,
)
from slack_sdk.socket_mode.request import SocketModeRequest
from slack_sdk.web import WebClient
from .connection import Connection, ConnectionState
from ..interval_runner import IntervalRunner
from ...errors import SlackClientConfigurationError


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

    current_session: Optional[Connection]
    current_session_state: ConnectionState
    current_session_runner: IntervalRunner

    current_app_monitor: IntervalRunner
    current_app_monitor_started: bool

    message_processor: IntervalRunner
    message_workers: ThreadPoolExecutor

    auto_reconnect_enabled: bool
    default_auto_reconnect_enabled: bool
    trace_enabled: bool
    receive_buffer_size: int  # bytes size

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
        all_message_trace_enabled: bool = False,
        ping_pong_trace_enabled: bool = False,
        ping_interval: float = 10,
        receive_buffer_size: int = 1024,
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
        self.all_message_trace_enabled = all_message_trace_enabled
        self.ping_pong_trace_enabled = ping_pong_trace_enabled
        self.ping_interval = ping_interval
        self.receive_buffer_size = receive_buffer_size
        if self.receive_buffer_size < 16:
            raise SlackClientConfigurationError(
                "Too small receive_buffer_size detected."
            )

        self.wss_uri = None
        self.message_queue = Queue()
        self.message_listeners = []
        self.socket_mode_request_listeners = []

        self.current_session = None
        self.current_session_state = ConnectionState()
        self.current_session_runner = IntervalRunner(
            self._run_current_session, 0.5
        ).start()

        self.current_app_monitor_started = False
        self.current_app_monitor = IntervalRunner(
            self._monitor_current_session, self.ping_interval
        )

        self.closed = False
        self.connect_operation_lock = Lock()

        self.message_processor = IntervalRunner(self.process_messages, 0.001).start()
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
        return self.current_session is not None and self.current_session.is_active()

    def connect(self) -> None:
        old_session: Optional[Connection] = self.current_session

        if self.wss_uri is None:
            self.wss_uri = self.issue_new_wss_url()

        self.current_session = Connection(
            url=self.wss_uri,
            logger=self.logger,
            ping_interval=self.ping_interval,
            trace_enabled=self.trace_enabled,
            all_message_trace_enabled=self.all_message_trace_enabled,
            ping_pong_trace_enabled=self.ping_pong_trace_enabled,
            receive_buffer_size=self.receive_buffer_size,
            proxy=self.proxy,
            on_message_listener=self._on_message,
            on_error_listener=self._on_error,
            on_close_listener=self._on_close,
        )
        self.current_session.connect()
        self.auto_reconnect_enabled = self.default_auto_reconnect_enabled

        if old_session is not None:
            old_session.close()
            self.current_session_state.terminated = True

        if not self.current_app_monitor_started:
            self.current_app_monitor_started = True
            self.current_app_monitor.start()

        self.logger.info(
            f"A new session has been established (session id: {self.session_id()})"
        )

    def disconnect(self) -> None:
        if self.current_session is not None:
            self.current_session.close()

    def send_message(self, message: str) -> None:
        if self.logger.level <= logging.DEBUG:
            self.logger.debug(
                f"Sending a message (session id: {self.session_id()}, message: {message})"
            )
        self.current_session.send(message)

    def close(self):
        self.closed = True
        self.auto_reconnect_enabled = False
        self.disconnect()
        if self.current_app_monitor.is_alive():
            self.current_app_monitor.shutdown()
        if self.message_processor.is_alive():
            self.message_processor.shutdown()
        self.message_workers.shutdown()

    def _on_message(self, message: str):
        if self.logger.level <= logging.DEBUG:
            self.logger.debug(f"on_message invoked: (message: {message})")
        self.enqueue_message(message)
        for listener in self.on_message_listeners:
            listener(message)

    def _on_error(self, error: Exception):
        self.logger.exception(
            f"on_error invoked (session id: {self.session_id()}, "
            f"error: {type(error).__name__}, message: {error})"
        )
        for listener in self.on_error_listeners:
            listener(error)

    def _on_close(self, code: int, reason: Optional[str] = None):
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

    def _run_current_session(self):
        try:
            if self.current_session is not None and self.current_session.is_active():
                self.logger.info(
                    "Starting to receive messages from a new connection"
                    f" (session id: {self.session_id()})"
                )
                self.current_session_state.terminated = False
                self.current_session.run_until_completion(self.current_session_state)
                self.logger.info(
                    "Stopped receiving messages from a connection"
                    f" (session id: {self.session_id()})"
                )
        except Exception as e:
            self.logger.exception(
                "Failed to start or stop the current session"
                f" (session id: {self.session_id()}, error: {e})"
            )

    def _monitor_current_session(self):
        if self.current_app_monitor_started:
            try:
                self.current_session.check_state()

                if self.auto_reconnect_enabled and (
                    self.current_session is None or not self.current_session.is_active()
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
