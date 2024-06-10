import asyncio
import logging
import time
import unittest
from random import randint
from threading import Thread

import pytest
from aiohttp import WSMessage

from slack_sdk.socket_mode.request import SocketModeRequest

from slack_sdk.socket_mode.async_client import AsyncBaseSocketModeClient

from slack_sdk.socket_mode.aiohttp import SocketModeClient
from slack_sdk.web.async_client import AsyncWebClient
from tests.slack_sdk.socket_mode.mock_socket_mode_server import (
    start_socket_mode_server,
    start_socket_mode_server_with_disconnection,
    socket_mode_envelopes,
    socket_mode_hello_message,
)
from tests.slack_sdk.socket_mode.mock_web_api_server import (
    setup_mock_web_api_server,
    cleanup_mock_web_api_server,
)
from tests.slack_sdk_async.helpers import async_test


class TestInteractionsAiohttp(unittest.TestCase):
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
        t = Thread(target=start_socket_mode_server(self, 3001))
        t.daemon = True
        t.start()

        received_messages = []
        received_socket_mode_requests = []

        async def message_handler(message: WSMessage):
            self.logger.info(f"Raw Message: {message}")
            await asyncio.sleep(randint(50, 200) / 1000)
            received_messages.append(message.data)

        async def socket_mode_listener(
            self: AsyncBaseSocketModeClient,
            request: SocketModeRequest,
        ):
            self.logger.info(f"Socket Mode Request: {request.payload}")
            await asyncio.sleep(randint(50, 200) / 1000)
            received_socket_mode_requests.append(request.payload)

        client = SocketModeClient(
            app_token="xapp-A111-222-xyz",
            web_client=self.web_client,
            on_message_listeners=[message_handler],
            auto_reconnect_enabled=False,
            trace_enabled=True,
        )
        client.socket_mode_request_listeners.append(socket_mode_listener)

        try:
            time.sleep(1)  # wait for the server
            client.wss_uri = "ws://0.0.0.0:3001/link"
            await client.connect()
            await asyncio.sleep(1)  # wait for the message receiver

            for _ in range(10):
                await client.send_message("foo")
                await client.send_message("bar")
                await client.send_message("baz")

            expected = socket_mode_envelopes + [socket_mode_hello_message] + ["foo", "bar", "baz"] * 10
            expected.sort()
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
    async def test_interactions_with_disconnection(self):
        t = Thread(target=start_socket_mode_server_with_disconnection(self, 3001))
        t.daemon = True
        t.start()

        self.disconnected = False
        received_messages = []
        received_socket_mode_requests = []

        async def message_handler(message: WSMessage):
            session_id = client.build_session_id(client.current_session)
            if "wait_for_disconnect" in message.data:
                return
            self.logger.info(f"Raw Message: {message}")
            await asyncio.sleep(randint(50, 200) / 1000)
            self.disconnected = "disconnect" in message.data
            received_messages.append(message.data + "_" + session_id)

        async def socket_mode_listener(
            self: AsyncBaseSocketModeClient,
            request: SocketModeRequest,
        ):
            self.logger.info(f"Socket Mode Request: {request.payload}")
            await asyncio.sleep(randint(50, 200) / 1000)
            received_socket_mode_requests.append(request.payload)

        client = SocketModeClient(
            app_token="xapp-A111-222-xyz",
            web_client=self.web_client,
            on_message_listeners=[message_handler],
            auto_reconnect_enabled=True,
            trace_enabled=True,
        )
        client.socket_mode_request_listeners.append(socket_mode_listener)

        try:
            time.sleep(1)  # wait for the server
            client.wss_uri = "ws://0.0.0.0:3001/link"
            await client.connect()
            await asyncio.sleep(1)  # wait for the message receiver

            # Because we want to check the expected messages of new session,
            # we need to ensure we send messaged after disconnected.
            count = 0
            while not self.disconnected and count < 10:
                try:
                    await client.send_message("wait_for_disconnect")
                except Exception as e:
                    self.logger.exception(e)
                finally:
                    await asyncio.sleep(1)
                    count += 1
            await asyncio.sleep(10)
            expected_session_id = client.build_session_id(client.current_session)

            for _ in range(10):
                await client.send_message("foo")
                await client.send_message("bar")
                await client.send_message("baz")

            expected = socket_mode_envelopes + [socket_mode_hello_message] + ["foo", "bar", "baz"] * 10
            expected.sort()

            count = 0
            while count < 10 and (
                len([msg for msg in received_messages if expected_session_id in msg]) < len(expected)
                or len(received_socket_mode_requests) < len(socket_mode_envelopes)
            ):
                await asyncio.sleep(0.2)
                count += 0.2

            received_messages.sort()

            # Only check messages of current alive session. Ignore the disconnected session.
            received_messages = [msg for msg in received_messages if expected_session_id in msg]
            expected = [msg + "_" + expected_session_id for msg in expected]

            self.assertEqual(received_messages, expected)

            self.assertEqual(len(socket_mode_envelopes), len(received_socket_mode_requests))
        finally:
            await client.close()
            self.loop.stop()
            t.join(timeout=5)

    @async_test
    async def test_send_message_while_disconnection(self):
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
            with pytest.raises(ConnectionError):
                await client.send_message("foo")

            await client.connect()
            await asyncio.sleep(1)  # wait for the message receiver
            await client.send_message("foo")
        finally:
            await client.close()
            self.loop.stop()
            t.join(timeout=5)
