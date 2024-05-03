import logging
import time
import unittest
from random import randint
from threading import Thread

import pytest

from slack_sdk.errors import SlackClientConfigurationError, SlackClientNotConnectedError
from slack_sdk.socket_mode.request import SocketModeRequest

from slack_sdk.socket_mode.client import BaseSocketModeClient

from slack_sdk import WebClient
from slack_sdk.socket_mode import SocketModeClient
from tests.slack_sdk.socket_mode.mock_socket_mode_server import (
    start_socket_mode_server,
    socket_mode_envelopes,
    socket_mode_hello_message,
)
from tests.slack_sdk.socket_mode.mock_web_api_server import (
    setup_mock_web_api_server,
    cleanup_mock_web_api_server,
)

import sys


class TestInteractionsBuiltin(unittest.TestCase):
    logger = logging.getLogger(__name__)

    def setUp(self):
        setup_mock_web_api_server(self)
        self.web_client = WebClient(
            token="xoxb-api_test",
            base_url="http://localhost:8888",
        )

    def tearDown(self):
        cleanup_mock_web_api_server(self)

    def test_buffer_size_validation(self):
        try:
            SocketModeClient(app_token="xapp-A111-222-xyz", receive_buffer_size=1)
            self.fail("SlackClientConfigurationError is expected here")
        except SlackClientConfigurationError:
            pass

    def test_interactions(self):
        default_recursion_limit = sys.getrecursionlimit()  # will restore later
        # This built-in WebSocket client internally has recursive method calls of _fetch_messages method.
        # In this test, the method calls can result in the following error when giving a quite small buffer size.
        # RecursionError: maximum recursion depth exceeded while calling a Python object
        # (the default recursion depth in Python is 1500)
        # Since the default buffer size is set to 1024, and it's enough to prevent the same situation happening,
        # we believe that the same situation never happens in the production usage.
        sys.setrecursionlimit(10000)

        t = Thread(target=start_socket_mode_server(self, 3011))
        t.daemon = True
        t.start()
        time.sleep(2)  # wait for the server

        try:
            buffer_size_list = [1024, 9000, 35, 49] + list([randint(16, 128) for _ in range(10)])
            for buffer_size in buffer_size_list:
                self.reset_server_state()

                received_messages = []
                received_socket_mode_requests = []

                def message_handler(message):
                    self.logger.info(f"Raw Message: {message}")
                    time.sleep(randint(50, 200) / 1000)
                    received_messages.append(message)

                def socket_mode_request_handler(client: BaseSocketModeClient, request: SocketModeRequest):
                    self.logger.info(f"Socket Mode Request: {request}")
                    time.sleep(randint(50, 200) / 1000)
                    received_socket_mode_requests.append(request)

                self.logger.info(f"Started testing with buffer size: {buffer_size}")
                client = SocketModeClient(
                    app_token="xapp-A111-222-xyz",
                    web_client=self.web_client,
                    on_message_listeners=[message_handler],
                    receive_buffer_size=buffer_size,
                    auto_reconnect_enabled=False,
                    trace_enabled=True,
                )
                try:
                    client.socket_mode_request_listeners.append(socket_mode_request_handler)
                    client.wss_uri = "ws://0.0.0.0:3011/link"
                    client.connect()
                    self.assertTrue(client.is_connected())
                    time.sleep(2)  # wait for the message receiver

                    repeat = 2
                    for _ in range(repeat):
                        client.send_message("foo")
                        client.send_message("bar")
                        client.send_message("baz")
                    self.assertTrue(client.is_connected())

                    expected = socket_mode_envelopes + [socket_mode_hello_message] + ["foo", "bar", "baz"] * repeat
                    expected.sort()

                    count = 0
                    while count < 5 and len(received_messages) < len(expected):
                        time.sleep(0.1)
                        self.logger.debug(f"Received messages: {len(received_messages)}")
                        count += 0.1

                    received_messages.sort()
                    self.assertEqual(len(received_messages), len(expected))
                    self.assertEqual(received_messages, expected)

                    self.assertEqual(len(socket_mode_envelopes), len(received_socket_mode_requests))
                finally:
                    pass
                    # client.close()
                self.logger.info(f"Passed with buffer size: {buffer_size}")

        finally:
            # Restore the default value
            sys.setrecursionlimit(default_recursion_limit)
            client.close()
            self.loop.stop()
            t.join(timeout=5)

        self.logger.info(f"Passed with buffer size: {buffer_size_list}")

    def test_send_message_while_disconnection(self):
        t = Thread(target=start_socket_mode_server(self, 3011))
        t.daemon = True
        t.start()
        time.sleep(2)  # wait for the server

        try:
            self.reset_server_state()
            client = SocketModeClient(
                app_token="xapp-A111-222-xyz",
                web_client=self.web_client,
                auto_reconnect_enabled=False,
                trace_enabled=True,
            )
            client.wss_uri = "ws://0.0.0.0:3011/link"
            client.connect()
            time.sleep(1)  # wait for the connection
            client.send_message("foo")

            client.disconnect()
            time.sleep(1)  # wait for the connection
            with pytest.raises(SlackClientNotConnectedError):
                client.send_message("foo")

            client.connect()
            time.sleep(1)  # wait for the connection
            client.send_message("foo")
        finally:
            client.close()
            self.loop.stop()
            t.join(timeout=5)
