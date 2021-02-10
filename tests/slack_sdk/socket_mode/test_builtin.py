import logging
import socket
import time
import unittest
from threading import Thread

from slack_sdk import WebClient
from slack_sdk.socket_mode import SocketModeClient
from slack_sdk.socket_mode.builtin.connection import Connection, ConnectionState
from slack_sdk.socket_mode.builtin.frame_header import FrameHeader
from slack_sdk.socket_mode.builtin.internals import (
    _generate_sec_websocket_key,
    _to_readable_opcode,
    _build_data_frame_for_sending,
    _parse_connect_response,
)
from slack_sdk.web.legacy_client import LegacyWebClient
from .mock_web_api_server import (
    setup_mock_web_api_server,
    cleanup_mock_web_api_server,
)


class TestBuiltin(unittest.TestCase):
    logger = logging.getLogger(__name__)

    def setUp(self):
        setup_mock_web_api_server(self)
        self.web_client = WebClient(
            token="xoxb-api_test",
            base_url="http://localhost:8888",
        )

    def tearDown(self):
        cleanup_mock_web_api_server(self)

    # ----------------------------------
    # SocketModeClient

    def test_init_close(self):
        on_message_listeners = [lambda message: None]
        client = SocketModeClient(
            app_token="xapp-A111-222-xyz", on_message_listeners=on_message_listeners
        )
        try:
            self.assertIsNotNone(client)
            self.assertFalse(client.is_connected())
            self.assertIsNone(client.session_id())  # not yet connected
        finally:
            client.close()

    def test_issue_new_wss_url(self):
        client = SocketModeClient(
            app_token="xapp-A111-222-xyz",
            web_client=self.web_client,
        )
        url = client.issue_new_wss_url()
        self.assertTrue(url.startswith("wss://"))

        legacy_client = LegacyWebClient(
            token="xoxb-api_test", base_url="http://localhost:8888"
        )
        response = legacy_client.apps_connections_open(app_token="xapp-A111-222-xyz")
        self.assertIsNotNone(response["url"])

    def test_connect_to_new_endpoint(self):
        client = SocketModeClient(
            app_token="xapp-A111-222-xyz",
            web_client=self.web_client,
        )
        client.connect_to_new_endpoint()
        self.assertFalse(client.is_connected())

    def test_enqueue_message(self):
        client = SocketModeClient(
            app_token="xapp-A111-222-xyz",
            web_client=self.web_client,
            on_message_listeners=[lambda message: None],
        )
        client.enqueue_message("hello")
        client.process_message()

        client.enqueue_message(
            """{"type":"hello","num_connections":1,"debug_info":{"host":"applink-111-222","build_number":10,"approximate_connection_time":18060},"connection_info":{"app_id":"A111"}}"""
        )
        client.process_message()

    # ----------------------------------
    # Connection

    def test_connection_init(self):
        conn = Connection(url="0.0.0.0", logger=self.logger)
        self.assertFalse(conn.is_active())
        state = ConnectionState()

        def run():
            conn.run_until_completion(state)

        t = Thread(target=run)
        t.start()

        time.sleep(0.5)
        state.terminated = True

        self.assertIsNotNone(conn)

    # ----------------------------------
    # FrameHeader

    def test_frame_header(self):
        fh = FrameHeader(0x1)
        self.assertIsNotNone(fh)

    # ----------------------------------
    # internals

    def test_generate_sec_websocket_key(self):
        key = _generate_sec_websocket_key()
        self.assertEqual(len(key), 24)

    def test_to_readable_opcode(self):
        res = _to_readable_opcode(FrameHeader.OPCODE_PONG)
        self.assertEqual(res, "pong")

    def test_build_data_frame_for_sending(self):
        res = _build_data_frame_for_sending("hello!", FrameHeader.OPCODE_TEXT)
        self.assertIsNotNone(res)

    def test_parse_connect_response(self):
        sock = socket.socket()
        try:
            sock.connect(("localhost", 8888))
            sock.send("""CONNECT localhost:8888 HTTP/1.0\r\n\r\n""".encode("utf-8"))
            status, text = _parse_connect_response(sock)
            self.assertEqual(status, 200)
            self.assertEqual(text, "HTTP/1.1 200 Connection established")
        finally:
            sock.close()
