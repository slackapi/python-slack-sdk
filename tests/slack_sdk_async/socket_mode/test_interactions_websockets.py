import asyncio
import logging
import time
import unittest
from random import randint
from threading import Thread
from typing import Optional

import pytest
from websockets.exceptions import WebSocketException

from slack_sdk.socket_mode.request import SocketModeRequest

from slack_sdk.socket_mode.async_client import AsyncBaseSocketModeClient
from slack_sdk.socket_mode.websockets import SocketModeClient
from slack_sdk.web.async_client import AsyncWebClient
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
from tests.slack_sdk_async.helpers import async_test


class TestInteractionsWebsockets(unittest.TestCase):
    logger = logging.getLogger(__name__)

    def setUp(self):
        setup_mock_web_api_server(self)
        self.web_client = AsyncWebClient(
            token="xoxb-api_test",
            base_url="http://localhost:8888",
        )

    def tearDown(self):
        cleanup_mock_web_api_server(self)

    @async_test
    async def test_interactions(self):
        t = Thread(target=start_socket_mode_server(self, 3002))
        t.daemon = True
        t.start()

        received_messages = []
        received_socket_mode_requests = []

        async def message_handler(
            receiver: AsyncBaseSocketModeClient,
            message: dict,
            raw_message: Optional[str],
        ):
            self.logger.info(f"Raw Message: {raw_message}")
            await asyncio.sleep(randint(50, 200) / 1000)
            received_messages.append(raw_message)

        async def socket_mode_listener(
            receiver: AsyncBaseSocketModeClient,
            request: SocketModeRequest,
        ):
            self.logger.info(f"Socket Mode Request: {request}")
            await asyncio.sleep(randint(50, 200) / 1000)
            received_socket_mode_requests.append(request)

        client = SocketModeClient(
            app_token="xapp-A111-222-xyz",
            web_client=self.web_client,
            auto_reconnect_enabled=False,
        )
        client.message_listeners.append(message_handler)
        client.socket_mode_request_listeners.append(socket_mode_listener)

        try:
            time.sleep(1)  # wait for the server
            client.wss_uri = "ws://0.0.0.0:3002/link"
            await client.connect()
            await asyncio.sleep(1)  # wait for the message receiver

            for _ in range(10):
                await client.send_message("foo")
                await client.send_message("bar")
                await client.send_message("baz")

            expected = socket_mode_envelopes + [socket_mode_hello_message] + ["foo", "bar", "baz"] * 10
            expected.sort()

            count = 0
            while count < 10 and (
                len(received_messages) < len(expected) or len(received_socket_mode_requests) < len(socket_mode_envelopes)
            ):
                await asyncio.sleep(0.2)
                count += 0.2

            received_messages.sort()
            self.assertEqual(received_messages, expected)

            self.assertEqual(len(socket_mode_envelopes), len(received_socket_mode_requests))
        finally:
            await client.close()
            self.loop.stop()
            t.join(timeout=5)

    @async_test
    async def test_send_message_while_disconnection(self):
        if is_ci_unstable_test_skip_enabled():
            # this test tends to fail on the GitHub Actions platform
            return
        t = Thread(target=start_socket_mode_server(self, 3001))
        t.daemon = True
        t.start()

        client = SocketModeClient(
            app_token="xapp-A111-222-xyz",
            web_client=self.web_client,
            auto_reconnect_enabled=False,
            trace_enabled=True,
        )

        try:
            time.sleep(1)  # wait for the server
            client.wss_uri = "ws://0.0.0.0:3001/link"
            await client.connect()
            await asyncio.sleep(1)  # wait for the message receiver
            await client.send_message("foo")

            await client.disconnect()
            await asyncio.sleep(1)  # wait for the message receiver
            with pytest.raises(WebSocketException):
                await client.send_message("foo")

            await client.connect()
            await asyncio.sleep(1)  # wait for the message receiver
            await client.send_message("foo")
        finally:
            await client.close()
            self.loop.stop()
            t.join(timeout=5)
