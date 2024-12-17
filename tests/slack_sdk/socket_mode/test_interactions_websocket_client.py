import logging
import time
import unittest
from random import randint

from websocket import WebSocketException

from slack_sdk.socket_mode.client import BaseSocketModeClient

from slack_sdk.socket_mode.request import SocketModeRequest

from slack_sdk import WebClient
from slack_sdk.socket_mode.websocket_client import SocketModeClient
from tests.slack_sdk.socket_mode.mock_socket_mode_server import (
    start_socket_mode_server,
    socket_mode_envelopes,
    socket_mode_hello_message,
    stop_socket_mode_server,
)
from tests.slack_sdk.socket_mode.mock_web_api_handler import MockHandler
from tests.mock_web_api_server import setup_mock_web_api_server, cleanup_mock_web_api_server


class TestInteractionsWebSocketClient(unittest.TestCase):
    logger = logging.getLogger(__name__)

    def setUp(self):
        setup_mock_web_api_server(self, MockHandler)
        self.web_client = WebClient(
            token="xoxb-api_test",
            base_url="http://localhost:8888",
        )
        start_socket_mode_server(self, 3012)

    def tearDown(self):
        cleanup_mock_web_api_server(self)
        stop_socket_mode_server(self)

    def test_interactions(self):
        received_messages = []
        received_socket_mode_requests = []

        def message_handler(ws_app, message):
            self.logger.info(f"Raw Message: {message}")
            time.sleep(randint(50, 200) / 1000)
            received_messages.append(message)

        def socket_mode_request_handler(client: BaseSocketModeClient, request: SocketModeRequest):
            self.logger.info(f"Socket Mode Request: {request}")
            time.sleep(randint(50, 200) / 1000)
            received_socket_mode_requests.append(request)

        client = SocketModeClient(
            app_token="xapp-A111-222-xyz",
            web_client=self.web_client,
            on_message_listeners=[message_handler],
            auto_reconnect_enabled=False,
            trace_enabled=True,
        )
        client.socket_mode_request_listeners.append(socket_mode_request_handler)

        try:
            client.wss_uri = "ws://0.0.0.0:3012/link"
            client.connect()
            time.sleep(1)  # wait for the message receiver
            self.assertTrue(client.is_connected())

            for _ in range(10):
                client.send_message("foo")
                client.send_message("bar")
                client.send_message("baz")
            self.assertTrue(client.is_connected())

            expected = socket_mode_envelopes + [socket_mode_hello_message] + ["foo", "bar", "baz"] * 10
            expected.sort()

            count = 0
            while count < 10 and (
                len(received_messages) < len(expected) or len(received_socket_mode_requests) < len(socket_mode_envelopes)
            ):
                time.sleep(0.2)
                count += 0.2

            received_messages.sort()
            self.assertEqual(received_messages, expected)

            self.assertEqual(len(socket_mode_envelopes), len(received_socket_mode_requests))
        finally:
            client.close()

    def test_send_message_while_disconnection(self):
        try:
            client = SocketModeClient(
                app_token="xapp-A111-222-xyz",
                web_client=self.web_client,
                auto_reconnect_enabled=False,
                trace_enabled=True,
            )
            client.wss_uri = "ws://0.0.0.0:3012/link"
            client.connect()
            time.sleep(1)  # wait for the connection
            client.send_message("foo")

            client.disconnect()
            time.sleep(1)  # wait for the connection
            try:
                client.send_message("foo")
                # TODO: The client may not raise an exception here
                # self.fail("WebSocketException is expected here")
            except WebSocketException as _:
                pass

            client.connect()
            time.sleep(1)  # wait for the connection
            client.send_message("foo")
        finally:
            client.close()
