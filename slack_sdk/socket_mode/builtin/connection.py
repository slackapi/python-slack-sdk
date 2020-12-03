import socket
import ssl
import struct
import time
from concurrent.futures.thread import ThreadPoolExecutor
from logging import Logger
from threading import Event
from typing import Optional, Callable, Union
from urllib.parse import urlparse
from uuid import uuid4

from slack_sdk.errors import SlackClientNotConnectedError
from .frame_header import FrameHeader
from .internals import (
    _open_new_socket,
    _parse_handshake_response,
    _validate_sec_websocket_accept,
    _generate_sec_websocket_key,
    _to_readable_opcode,
    _receive,
    _build_data_frame_for_sending,
)


class Connection:
    url: str
    logger: Logger
    proxy: Optional[str]
    ping_interval: float
    last_ping_pong_time: Optional[float]
    trace_enabled: bool
    session_id: str
    sock: Optional[ssl.SSLSocket]
    sock_monitor: ThreadPoolExecutor
    message_receiver: ThreadPoolExecutor

    on_message_listener: Optional[Callable[[str], None]]
    on_error_listener: Optional[Callable[[Exception], None]]
    on_close_listener: Optional[Callable[[int, Optional[str]], None]]

    def __init__(
        self,
        url: str,
        logger: Logger,
        proxy: Optional[str] = None,
        ping_interval: float = 10,  # seconds
        receive_timeout: float = 5,
        trace_enabled: bool = False,
        on_message_listener: Optional[Callable[[str], None]] = None,
        on_error_listener: Optional[Callable[[Exception], None]] = None,
        on_close_listener: Optional[Callable[[int, Optional[str]], None]] = None,
    ):
        self.url = url
        self.logger = logger
        self.proxy = proxy

        self.ping_interval = ping_interval
        self.receive_timeout = receive_timeout
        self.session_id = str(uuid4())
        self.trace_enabled = trace_enabled
        self.sock = None
        self.sock_monitor = ThreadPoolExecutor(1)
        self.sock_monitor.submit(self._monitor_current_session)
        self.last_ping_pong_time = None
        self.message_receiver = ThreadPoolExecutor(1)
        self.message_receiver.submit(self._keep_receiving_messages)

        self.on_message_listener = on_message_listener
        self.on_error_listener = on_error_listener
        self.on_close_listener = on_close_listener

    def connect(self) -> None:
        sock: Optional[ssl.SSLSocket] = None
        try:
            url = (self.proxy or self.url).strip()
            parsed_url = urlparse(url)
            sock = _open_new_socket(parsed_url.hostname)

            hostname: str = parsed_url.hostname
            port: int = parsed_url.port or (
                443 if url.startswith("https://") or url.startswith("wss://") else 80
            )
            if self.trace_enabled:
                self.logger.debug(
                    f"Connecting to the address for handshake: {hostname}:{port} "
                    f"(session id: {self.session_id})"
                )

            sock.connect((hostname, port))

            # WebSocket handshake
            try:
                path = f"{parsed_url.path}?{parsed_url.query}"
                sec_websocket_key = _generate_sec_websocket_key()
                message = f"""GET {path} HTTP/1.1
                    Host: {parsed_url.hostname}
                    Upgrade: websocket
                    Connection: Upgrade
                    Sec-WebSocket-Key: {sec_websocket_key}
                    Sec-WebSocket-Version: 13

                """
                req: str = "\r\n".join([line.lstrip() for line in message.split("\n")])
                if self.trace_enabled:
                    self.logger.debug(
                        f"Socket Mode handshake request (session id: {self.session_id}):\n{req}"
                    )
                sock.send(req.encode("utf-8"))
                sock.settimeout(self.receive_timeout)
                status, headers, text = _parse_handshake_response(sock)
                if self.trace_enabled:
                    self.logger.debug(
                        f"Socket Mode handshake response (session id: {self.session_id}):\n{text}"
                    )
                # HTTP/1.1 101 Switching Protocols
                if status == 101:
                    if not _validate_sec_websocket_accept(sec_websocket_key, headers):
                        raise SlackClientNotConnectedError(
                            "Invalid response header detected in Socket Mode handshake response"
                            f" (session id: {self.session_id})"
                        )
                    # set this successfully connected socket
                    self.sock = sock
                    self.ping(f"{self.session_id}:{time.time()}")
                else:
                    message = (
                        f"Received an unexpected response for handshake "
                        f"(status: {status}, response: {text}, session id: {self.session_id})"
                    )
                    self.logger.warning(message)

            except socket.error as e:
                code: Optional[int] = None
                if e.args and len(e.args) > 1 and isinstance(e.args[0], int):
                    code = e.args[0]
                if code is not None:
                    self.logger.exception(
                        f"Error code: {code} (session id: {self.session_id}, error: {e})"
                    )
                raise

        except Exception as e:
            self.logger.exception(
                f"Failed to establish a connection (session id: {self.session_id}, error: {e})"
            )
            self.disconnect()

    def disconnect(self) -> None:
        if self.sock is not None:
            self.sock.close()
            self.sock = None
        self.logger.info(
            f"The connection has been closed (session id: {self.session_id})"
        )

    def run_forever(self) -> None:
        if not self.is_active():
            self.connect()
        Event().wait()

    def is_active(self) -> bool:
        return self.sock is not None

    def close(self) -> None:
        self.disconnect()
        self.sock_monitor.shutdown()
        self.message_receiver.shutdown()

    def ping(self, payload: Union[str, bytes] = "") -> None:
        if self.trace_enabled:
            if isinstance(payload, bytes):
                payload = payload.decode("utf-8")
            self.logger.debug(
                "Sending a ping data frame "
                f"(session id: {self.session_id}, payload: {payload})"
            )
        data = _build_data_frame_for_sending(payload, FrameHeader.OPCODE_PING)
        self.sock.send(data)

    def pong(self, payload: Union[str, bytes] = "") -> None:
        if self.trace_enabled:
            if isinstance(payload, bytes):
                payload = payload.decode("utf-8")
            self.logger.debug(
                "Sending a pong data frame "
                f"(session id: {self.session_id}, payload: {payload})"
            )
        data = _build_data_frame_for_sending(payload, FrameHeader.OPCODE_PONG)
        self.sock.send(data)

    def send(self, payload: str) -> None:
        if self.trace_enabled:
            if isinstance(payload, bytes):
                payload = payload.decode("utf-8")
            self.logger.debug(
                "Sending a text data frame "
                f"(session id: {self.session_id}, payload: {payload})"
            )
        data = _build_data_frame_for_sending(payload, FrameHeader.OPCODE_TEXT)
        self.sock.send(data)

    # ---------------------------------------------------

    def _keep_receiving_messages(self):
        while True:
            try:
                if self.is_active():
                    header, data = _receive(self.sock)
                    if self.trace_enabled:
                        opcode = _to_readable_opcode(header.opcode) if header else "-"
                        payload = data.decode("utf-8") if data is not None else ""
                        self.logger.debug(
                            "Received a new data frame "
                            f"(session id: {self.session_id}, opcode: {opcode}, payload: {payload})"
                        )

                    if header is not None:
                        if header.opcode == FrameHeader.OPCODE_PING:
                            self.pong(data)
                        elif header.opcode == FrameHeader.OPCODE_PONG:
                            elements = data.decode("utf-8").split(":")
                            if len(elements) >= 2:
                                session_id, ping_time = elements[0], elements[1]
                                if self.session_id == session_id:
                                    self.last_ping_pong_time = float(ping_time)
                        elif header.opcode == FrameHeader.OPCODE_TEXT:
                            if self.on_message_listener is not None:
                                text = data.decode("utf-8")
                                self.on_message_listener(text)
                        elif header.opcode == FrameHeader.OPCODE_CLOSE:
                            if self.on_close_listener is not None:
                                if len(data) >= 2:
                                    (code,) = struct.unpack("!H", data[:2])
                                    reason = data[2:].decode("utf-8")
                                    self.on_close_listener(code, reason)
                                else:
                                    self.on_close_listener(1005, "")
                            self.disconnect()
                        else:
                            opcode = (
                                _to_readable_opcode(header.opcode) if header else "-"
                            )
                            payload = data.decode("utf-8") if data is not None else ""
                            message = (
                                "Received an unsupported data frame "
                                f"(session id: {self.session_id}, opcode: {opcode}, payload: {payload})"
                            )
                            self.logger.warning(message)
                else:
                    time.sleep(1)
            except socket.timeout:
                time.sleep(0.01)
            except Exception as e:
                if self.on_error_listener is not None:
                    self.on_error_listener(e)
                else:
                    self.logger.exception(e)

    def _monitor_current_session(self):
        while True:
            time.sleep(self.ping_interval)
            try:
                if self.sock is not None:
                    is_stale = (
                        self.last_ping_pong_time is not None
                        and time.time() - self.last_ping_pong_time
                        > self.ping_interval * 2
                    )
                    if is_stale:
                        self.logger.info(
                            "The connection seems to be stale. Disconnecting..."
                            f" (session id: {self.session_id})"
                        )
                        self.disconnect()
                        break
                    else:
                        self.ping(f"{self.session_id}:{time.time()}")
                else:
                    self.logger.info(
                        "This connection is already closed."
                        f" (session id: {self.session_id})"
                    )
                    break
            except Exception as e:
                self.logger.exception(
                    "Failed to check the state of sock "
                    f"(session id: {self.session_id}, error: {type(e).__name__}, message: {e})"
                )
