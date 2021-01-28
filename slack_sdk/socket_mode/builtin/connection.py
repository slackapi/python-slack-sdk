import socket
import ssl
import struct
import time
from logging import Logger
from typing import Optional, Callable, Union, List, Tuple
from urllib.parse import urlparse
from uuid import uuid4

from slack_sdk.errors import SlackClientNotConnectedError, SlackClientConfigurationError
from .frame_header import FrameHeader
from .internals import (
    _open_new_socket,
    _parse_handshake_response,
    _validate_sec_websocket_accept,
    _generate_sec_websocket_key,
    _to_readable_opcode,
    _receive_messages,
    _build_data_frame_for_sending,
    _parse_text_payload,
)


class ConnectionState:
    # The flag supposed to be used for telling SocketModeClient
    # when this connection is no longer available
    terminated: bool

    def __init__(self):
        self.terminated = False


class Connection:
    url: str
    logger: Logger
    proxy: Optional[str]

    trace_enabled: bool
    ping_pong_trace_enabled: bool
    last_ping_pong_time: Optional[float]

    session_id: str
    sock: Optional[ssl.SSLSocket]

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
        receive_buffer_size: int = 1024,
        trace_enabled: bool = False,
        all_message_trace_enabled: bool = False,
        ping_pong_trace_enabled: bool = False,
        on_message_listener: Optional[Callable[[str], None]] = None,
        on_error_listener: Optional[Callable[[Exception], None]] = None,
        on_close_listener: Optional[Callable[[int, Optional[str]], None]] = None,
        connection_type_name: str = "Socket Mode",
    ):
        self.url = url
        self.logger = logger
        self.proxy = proxy

        self.ping_interval = ping_interval
        self.receive_timeout = receive_timeout
        self.receive_buffer_size = receive_buffer_size
        if self.receive_buffer_size < 16:
            raise SlackClientConfigurationError(
                "Too small receive_buffer_size detected."
            )

        self.session_id = str(uuid4())
        self.trace_enabled = trace_enabled
        self.all_message_trace_enabled = all_message_trace_enabled
        self.ping_pong_trace_enabled = ping_pong_trace_enabled
        self.last_ping_pong_time = None
        self.consecutive_check_state_error_count = 0
        self.sock = None

        self.on_message_listener = on_message_listener
        self.on_error_listener = on_error_listener
        self.on_close_listener = on_close_listener
        self.connection_type_name = connection_type_name

    def connect(self) -> None:
        try:
            url = (self.proxy or self.url).strip()
            parsed_url = urlparse(url)

            hostname: str = parsed_url.hostname
            port: int = parsed_url.port or (
                443 if url.startswith("https://") or url.startswith("wss://") else 80
            )
            if self.trace_enabled:
                self.logger.debug(
                    f"Connecting to the address for handshake: {hostname}:{port} "
                    f"(session id: {self.session_id})"
                )
            sock: Union[ssl.SSLSocket, socket] = _open_new_socket(
                server_hostname=parsed_url.hostname,
                server_port=port,
                logger=self.logger,
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
                        f"{self.connection_type_name} handshake request (session id: {self.session_id}):\n{req}"
                    )
                sock.send(req.encode("utf-8"))
                sock.settimeout(self.receive_timeout)
                status, headers, text = _parse_handshake_response(sock)
                if self.trace_enabled:
                    self.logger.debug(
                        f"{self.connection_type_name} handshake response (session id: {self.session_id}):\n{text}"
                    )
                # HTTP/1.1 101 Switching Protocols
                if status == 101:
                    if not _validate_sec_websocket_accept(sec_websocket_key, headers):
                        raise SlackClientNotConnectedError(
                            f"Invalid response header detected in {self.connection_type_name} handshake response"
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

    def is_active(self) -> bool:
        return self.sock is not None

    def close(self) -> None:
        self.disconnect()

    def ping(self, payload: Union[str, bytes] = "") -> None:
        if self.trace_enabled and self.ping_pong_trace_enabled:
            if isinstance(payload, bytes):
                payload = payload.decode("utf-8")
            self.logger.debug(
                "Sending a ping data frame "
                f"(session id: {self.session_id}, payload: {payload})"
            )
        data = _build_data_frame_for_sending(payload, FrameHeader.OPCODE_PING)
        self.sock.send(data)

    def pong(self, payload: Union[str, bytes] = "") -> None:
        if self.trace_enabled and self.ping_pong_trace_enabled:
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

    def check_state(self) -> None:
        try:
            if self.sock is not None:
                is_stale = (
                    self.last_ping_pong_time is not None
                    and time.time() - self.last_ping_pong_time > self.ping_interval * 2
                )
                if is_stale:
                    self.logger.info(
                        "The connection seems to be stale. Disconnecting..."
                        f" (session id: {self.session_id})"
                    )
                    self.disconnect()
                else:
                    self.ping(f"{self.session_id}:{time.time()}")
            else:
                self.logger.debug(
                    "This connection is already closed."
                    f" (session id: {self.session_id})"
                )
            self.consecutive_check_state_error_count = 0
        except Exception as e:
            self.logger.exception(
                "Failed to check the state of sock "
                f"(session id: {self.session_id}, error: {type(e).__name__}, message: {e})"
            )
            self.consecutive_check_state_error_count += 1
            if self.consecutive_check_state_error_count >= 5:
                self.disconnect()

    def run_until_completion(self, state: ConnectionState) -> None:
        repeated_messages = {"payload": 0}
        ping_count = 0
        pong_count = 0
        ping_pong_log_summary_size = 1000
        while not state.terminated:
            try:
                if self.is_active():
                    received_messages: List[
                        Tuple[Optional[FrameHeader], bytes]
                    ] = _receive_messages(
                        sock=self.sock,
                        logger=self.logger,
                        receive_buffer_size=self.receive_buffer_size,
                        all_message_trace_enabled=self.all_message_trace_enabled,
                    )
                    for message in received_messages:
                        header, data = message

                        # -----------------
                        # trace logging

                        if self.trace_enabled is True:
                            opcode: str = (
                                _to_readable_opcode(header.opcode) if header else "-"
                            )
                            payload: str = _parse_text_payload(data, self.logger)
                            count: Optional[int] = repeated_messages.get(payload)
                            if count is None:
                                count = 1
                            else:
                                count += 1
                            repeated_messages = {payload: count}
                            if (
                                not self.ping_pong_trace_enabled
                                and header is not None
                                and header.opcode is not None
                            ):
                                if header.opcode == FrameHeader.OPCODE_PING:
                                    ping_count += 1
                                    if ping_count % ping_pong_log_summary_size == 0:
                                        self.logger.debug(
                                            f"Received {ping_pong_log_summary_size} ping data frame "
                                            f"(session id: {self.session_id})"
                                        )
                                        ping_count = 0
                                if header.opcode == FrameHeader.OPCODE_PONG:
                                    pong_count += 1
                                    if pong_count % ping_pong_log_summary_size == 0:
                                        self.logger.debug(
                                            f"Received {ping_pong_log_summary_size} pong data frame "
                                            f"(session id: {self.session_id})"
                                        )
                                        pong_count = 0

                            ping_pong_to_skip = (
                                header is not None
                                and header.opcode is not None
                                and (
                                    header.opcode == FrameHeader.OPCODE_PING
                                    or header.opcode == FrameHeader.OPCODE_PONG
                                )
                                and not self.ping_pong_trace_enabled
                            )
                            if not ping_pong_to_skip and count < 5:
                                # if so many same payloads came in, the trace logging should be skipped.
                                # e.g., after receiving "UNAUTHENTICATED: cache_error", many "opcode: -, payload: "
                                self.logger.debug(
                                    "Received a new data frame "
                                    f"(session id: {self.session_id}, opcode: {opcode}, payload: {payload})"
                                )

                        if header is None:
                            # Skip no header message
                            continue

                        # -----------------
                        # message with opcode

                        if header.opcode == FrameHeader.OPCODE_PING:
                            self.pong(data)
                        elif header.opcode == FrameHeader.OPCODE_PONG:
                            str_message = data.decode("utf-8")
                            elements = str_message.split(":")
                            if len(elements) >= 2:
                                session_id, ping_time = elements[0], elements[1]
                                if self.session_id == session_id:
                                    try:
                                        self.last_ping_pong_time = float(ping_time)
                                    except Exception as e:
                                        self.logger.debug(
                                            "Failed to parse a pong message "
                                            f" (message: {str_message}, error: {e}"
                                        )
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
                            state.terminated = True
                        else:
                            # Just warn logging
                            opcode = (
                                _to_readable_opcode(header.opcode) if header else "-"
                            )
                            payload: Union[bytes, str] = data
                            if header.opcode != FrameHeader.OPCODE_BINARY:
                                try:
                                    payload = (
                                        data.decode("utf-8") if data is not None else ""
                                    )
                                except Exception as e:
                                    self.logger.info(
                                        f"Failed to convert the data to text {e}"
                                    )
                            message = (
                                "Received an unsupported data frame "
                                f"(session id: {self.session_id}, opcode: {opcode}, payload: {payload})"
                            )
                            self.logger.warning(message)
                else:
                    time.sleep(0.2)
            except socket.timeout:
                time.sleep(0.01)
            except OSError as e:
                # getting errno.EBADF and the socket is no longer available
                if e.errno == 9 and state.terminated:
                    self.logger.debug(
                        "The reason why you got [Errno 9] Bad file descriptor here is "
                        "the socket is no longer available."
                    )
                else:
                    if self.on_error_listener is not None:
                        self.on_error_listener(e)
                    else:
                        self.logger.exception(
                            "Got an OSError while receiving data"
                            f" (session id: {self.session_id}, error: {e})"
                        )
                # As this connection no longer works in any way, terminating it
                if self.is_active():
                    try:
                        self.disconnect()
                    except Exception as disconnection_error:
                        self.logger.exception(
                            "Failed to disconnect"
                            f" (session id: {self.session_id}, error: {disconnection_error})"
                        )
                state.terminated = True
                break
            except Exception as e:
                if self.on_error_listener is not None:
                    self.on_error_listener(e)
                else:
                    self.logger.exception(
                        "Got an exception while receiving data"
                        f" (session id: {self.session_id}, error: {e})"
                    )

        state.terminated = True
