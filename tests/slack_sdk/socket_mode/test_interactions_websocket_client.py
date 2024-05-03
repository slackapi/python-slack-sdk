import logging
import time
import unittest
from random import randint
from threading import Thread

from websocket import WebSocketException

from slack_sdk.socket_mode.client import BaseSocketModeClient

from slack_sdk.socket_mode.request import SocketModeRequest

from slack_sdk import WebClient
from slack_sdk.socket_mode.websocket_client import SocketModeClient
from tests.helpers import is_ci_unstable_test_skip_enabled
from tests.slack_sdk.socket_mode.mock_socket_mode_server import (
    start_socket_mode_server,
    socket_mode_envelopes,
    socket_mode_hello_message,
)
from tests.slack_sdk.socket_mode.mock_web_api_server import (
    setup_mock_web_api_server,
    cleanup_mock_web_api_server,
)


class TestInteractionsWebSocketClient(unittest.TestCase):
    logger = logging.getLogger(__name__)

    def setUp(self):
        setup_mock_web_api_server(self)
        self.web_client = WebClient(
            token="xoxb-api_test",
            base_url="http://localhost:8888",
        )

    def tearDown(self):
        cleanup_mock_web_api_server(self)

    def test_interactions(self):
        t = Thread(target=start_socket_mode_server(self, 3012))
        t.daemon = True
        t.start()

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
            time.sleep(1)  # wait for the server
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
            self.loop.stop()
            t.join(timeout=5)

    def test_send_message_while_disconnection(self):
        if is_ci_unstable_test_skip_enabled():
            # this test tends to fail on the GitHub Actions platform
            return
        t = Thread(target=start_socket_mode_server(self, 3012))
        t.daemon = True
        t.start()
        time.sleep(2)  # wait for the server

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
            self.loop.stop()
            t.join(timeout=5)
