import hashlib
import itertools
import os
import random
import socket
import ssl
import struct
from base64 import encodebytes
from hmac import compare_digest
from typing import Tuple, Optional, Union, List

from .frame_header import FrameHeader


def _open_new_socket(server_hostname: str) -> ssl.SSLSocket:
    sock = socket.socket(family=ssl.AF_INET, type=ssl.SOCK_STREAM)
    sock.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
    sock.setsockopt(socket.SOL_TCP, socket.TCP_KEEPINTVL, 10)
    sock.setsockopt(socket.SOL_TCP, socket.TCP_KEEPCNT, 3)

    sock = ssl.SSLContext(ssl.PROTOCOL_SSLv23).wrap_socket(
        sock,
        do_handshake_on_connect=True,
        suppress_ragged_eofs=True,
        server_hostname=server_hostname,
    )
    sock.settimeout(5)
    return sock


def _read_http_response_line(sock: ssl.SSLSocket) -> str:
    cs = []
    while True:
        c: str = sock.recv(1).decode("utf-8")
        if c == "\r":
            break
        if c != "\n":
            cs.append(c)
    return "".join(cs)


def _parse_handshake_response(sock: ssl.SSLSocket) -> (int, dict, str):
    """Parses the handshake response.

    :param sock: the current socket
    :return: (http status, headers, whole response as a str)
    """
    lines = []
    status = None
    headers = {}
    while True:
        line = _read_http_response_line(sock)
        if status is None:
            elements = line.split(" ")
            if len(elements) > 2:
                status = int(elements[1])
        else:
            elements = line.split(":")
            if len(elements) == 2:
                headers[elements[0].strip().lower()] = elements[1].strip()
        if line is None or len(line) == 0:
            break
        lines.append(line)
    text = "\n".join(lines)
    return (status, headers, text)


def _generate_sec_websocket_key() -> str:
    return encodebytes(os.urandom(16)).decode("utf-8").strip()


def _validate_sec_websocket_accept(sec_websocket_key: str, headers: dict) -> bool:
    v = (sec_websocket_key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").encode("utf-8")
    expected = encodebytes(hashlib.sha1(v).digest()).decode("utf-8").strip()
    actual = headers.get("sec-websocket-accept").strip()
    return compare_digest(expected, actual)


def _to_readable_opcode(opcode: int) -> str:
    if opcode == FrameHeader.OPCODE_CONTINUATION:
        return "continuation"
    if opcode == FrameHeader.OPCODE_TEXT:
        return "text"
    if opcode == FrameHeader.OPCODE_BINARY:
        return "binary"
    if opcode == FrameHeader.OPCODE_CLOSE:
        return "close"
    if opcode == FrameHeader.OPCODE_PING:
        return "ping"
    if opcode == FrameHeader.OPCODE_PONG:
        return "pong"


def _receive(sock: ssl.SSLSocket) -> Tuple[Optional[FrameHeader], bytes]:
    buf_size = 1024
    length = 0
    mask_key: Optional[str] = None
    header: Optional[FrameHeader] = None
    data: bytes = bytes()
    while True:
        bs: bytes = sock.recv(buf_size)
        if bs is None or len(bs) == 0:
            break
        idx_after_length = 0
        if header is None:
            if len(bs) < 2:
                return (None, bs)

            # https://tools.ietf.org/html/rfc6455#section-5.2
            b1, b2 = bs[0], bs[1]
            _length = b2 & 0b01111111
            length = _length
            idx_after_length = 2
            if _length == 126:
                length = struct.unpack("!H", bytes(bs[2:4]))[0]
                idx_after_length = 4
            elif _length == 127:
                length = struct.unpack("!H", bytes(bs[2:10]))[0]
                idx_after_length = 10

            header = FrameHeader(
                fin=b1 & 0b10000000,
                rsv1=b1 & 0b01000000,
                rsv2=b1 & 0b00100000,
                rsv3=b1 & 0b00010000,
                opcode=b1 & 0b00001111,
                masked=b2 & 0b10000000,
                length=length,
            )
            if header.masked > 0:
                if mask_key is None:
                    idx1, idx2 = idx_after_length, idx_after_length + 4
                    mask_key = bs[idx1:idx2]
                    idx_after_length += 4

        received_data = bs[idx_after_length:] if idx_after_length > 0 else bs
        if header.masked > 0:
            for i in range(received_data):
                mask = mask_key[i % 4]
                received_data[i] ^= mask
            data += received_data
        else:
            data += received_data

        if len(data) >= length:
            break

    return (header, data)


def _build_data_frame_for_sending(
    payload: Union[str, bytes],
    opcode: int,
    fin: int = 1,
    rsv1: int = 0,
    rsv2: int = 0,
    rsv3: int = 0,
    masked: int = 1,
):
    b1 = fin << 7 | rsv1 << 6 | rsv2 << 5 | rsv3 << 4 | opcode
    header: bytes = bytes([b1])

    original_payload_data: bytes = payload.encode("utf-8") if isinstance(
        payload, str
    ) else payload
    payload_length = len(original_payload_data)
    if payload_length <= 125:
        b2 = masked << 7 | payload_length
        header += bytes([b2])
    else:
        b2 = masked << 7 | 126
        header += struct.pack("!BH", b2, payload_length)

    mask_key: List[int] = random.choices(range(256), k=4)
    header += bytes(mask_key)

    payload_data: bytes = bytes(
        byte ^ mask
        for byte, mask in zip(original_payload_data, itertools.cycle(mask_key))
    )
    return header + payload_data
