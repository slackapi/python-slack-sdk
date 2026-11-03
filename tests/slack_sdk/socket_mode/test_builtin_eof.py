import errno
import logging
import random
import socket
import struct
import threading
import unittest
from unittest.mock import Mock

from slack_sdk.socket_mode.builtin.connection import Connection, ConnectionState
from slack_sdk.socket_mode.builtin.internals import _receive_messages


class TestBuiltinEOF(unittest.TestCase):
    def test_closed_socket_errors_terminate_without_losing_complete_messages(self):
        for code in (errno.EBADF, errno.ENOTSOCK):
            with self.subTest(code=code):
                with self.assertRaises(ConnectionError):
                    self.receive([OSError(code, "closed")])
                self.assertEqual(
                    self.receive([b"\x81\x02ok\x81\x05ab", OSError(code, "closed")]),
                    [(1, b"ok")],
                )

    def test_random_transport_chunk_boundaries(self):
        rng = random.Random(1246)
        payloads = [b"", b"hello", b"a" * 126, b"b" * 1024]
        frames = [b"\x81\x00", b"\x81\x05hello"]
        frames += [b"\x81\x7e" + struct.pack("!H", len(p)) + p for p in payloads[2:]]
        wire = b"".join(frames)
        for iteration in range(100):
            with self.subTest(iteration=iteration):
                chunks, offset = [], 0
                while offset < len(wire):
                    size = rng.randint(1, 64)
                    chunks.append(wire[offset : offset + size])
                    offset += size
                sock = Mock()
                sock.recv.side_effect = chunks + [b""]
                received = []
                while True:
                    try:
                        received += _receive_messages(sock, threading.Lock(), logging.getLogger(__name__))
                    except ConnectionError:
                        break
                self.assertEqual([(h.opcode, data) for h, data in received], [(1, p) for p in payloads])

    def test_real_socket_delivers_complete_message_before_eof(self):
        self.run_socket_case(b"\x81\x02ok\x81\x05ab", ["ok"], [], 1)

    def test_real_socket_empty_close_is_not_reported_as_error(self):
        self.run_socket_case(b"\x81\x02ok\x88\x00", ["ok"], [(1005, "")], 0)

    def run_socket_case(self, wire, expected_messages, expected_closes, error_count):
        local, peer = socket.socketpair()
        local.settimeout(0.1)
        messages, closes, errors = [], [], []
        connection = Connection(
            url="ws://localhost",
            logger=logging.getLogger(__name__),
            on_message_listener=messages.append,
            on_close_listener=lambda code, reason: closes.append((code, reason)),
            on_error_listener=errors.append,
        )
        connection.sock = local
        state = ConnectionState()
        peer.sendall(wire)
        peer.shutdown(socket.SHUT_WR)
        worker = threading.Thread(target=connection.run_until_completion, args=(state,), daemon=True)
        worker.start()
        try:
            worker.join(timeout=1)
            self.assertFalse(worker.is_alive())
            self.assertEqual(messages, expected_messages)
            self.assertEqual(closes, expected_closes)
            self.assertEqual(len(errors), error_count)
            self.assertTrue(state.terminated)
            self.assertFalse(connection.is_active())
        finally:
            state.terminated = True
            peer.close()
            worker.join(timeout=1)
            connection.close()

    def test_eof_during_header_preserves_only_complete_messages(self):
        for partial in (b"\x81", b"\x81\x7e\x00", b"\x81\x7f\x00\x00"):
            with self.subTest(partial=partial):
                self.assertEqual(self.receive([b"\x81\x02ok" + partial, b""]), [(1, b"ok")])
                with self.assertRaises(ConnectionError):
                    self.receive([partial, b""])

    def test_extended_header_split_across_many_reads(self):
        self.assertEqual(self.receive([b"\x81\x7e", b"\x00", b"\x03", b"hey"]), [(1, b"hey")])

    def receive(self, chunks):
        sock = Mock()
        sock.recv.side_effect = chunks
        result = _receive_messages(sock, threading.Lock(), logging.getLogger(__name__))
        for call in sock.recv.call_args_list:
            self.assertGreater(call.args[0], 0)
        return [(header.opcode, data) for header, data in result]

    def test_empty_frames_do_not_read_past_the_frame(self):
        for opcode in (1, 8, 9, 10):
            with self.subTest(opcode=opcode):
                self.assertEqual(self.receive([bytes([0x80 | opcode, 0])]), [(opcode, b"")])

    def test_complete_messages_survive_eof_during_next_payload(self):
        self.assertEqual(self.receive([b"\x81\x02ok\x81\x05ab", b""]), [(1, b"ok")])

    def test_incomplete_message_is_not_delivered(self):
        with self.assertRaises(ConnectionError):
            self.receive([b"\x81\x05ab", b""])

    def test_split_message(self):
        self.assertEqual(self.receive([b"\x81", b"\x05h", b"ello"]), [(1, b"hello")])

    def test_timeout_is_not_eof(self):
        with self.assertRaises(socket.timeout):
            self.receive([socket.timeout()])

    def test_transport_eof_terminates_receiver(self):
        local, peer = socket.socketpair()
        connection = Connection(url="ws://localhost", logger=logging.getLogger(__name__))
        connection.sock = local
        state = ConnectionState()
        peer.close()
        worker = threading.Thread(target=connection.run_until_completion, args=(state,), daemon=True)
        worker.start()
        try:
            worker.join(timeout=0.5)
            self.assertFalse(worker.is_alive(), "EOF must terminate the receiver instead of spinning")
            self.assertTrue(state.terminated)
            self.assertFalse(connection.is_active())
        finally:
            state.terminated = True
            worker.join(timeout=1)
            connection.close()
