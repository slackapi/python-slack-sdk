import asyncio
import logging
import unittest
from unittest.mock import MagicMock, patch

import aiohttp

from slack_sdk.socket_mode.aiohttp import SocketModeClient
from slack_sdk.web.async_client import AsyncWebClient
from tests.slack_sdk.socket_mode.mock_web_api_handler import MockHandler
from tests.slack_sdk_async.helpers import async_test
from tests.mock_web_api_server import setup_mock_web_api_server_async, cleanup_mock_web_api_server_async


class TestAiohttp(unittest.TestCase):
    def setUp(self):
        setup_mock_web_api_server_async(self, MockHandler)
        self.web_client = AsyncWebClient(
            token="xoxb-api_test",
            base_url="http://localhost:8888",
        )

    def tearDown(self):
        cleanup_mock_web_api_server_async(self)

    @async_test
    async def test_init_close(self):
        client = SocketModeClient(
            app_token="xapp-A111-222-xyz",
            web_client=self.web_client,
            auto_reconnect_enabled=False,
        )
        try:
            self.assertIsNotNone(client)
        finally:
            await client.close()

    @async_test
    async def test_connect_returns_when_closed(self):
        # Regression test for #1913: connect() must not loop forever once the client is closed.
        client = SocketModeClient(
            app_token="xapp-A111-222-xyz",
            web_client=self.web_client,
            auto_reconnect_enabled=False,
            ping_interval=0.01,
        )
        client.wss_uri = "ws://localhost:8888/link"
        await client.close()
        await asyncio.wait_for(client.connect(), timeout=1.0)
        self.assertTrue(client.closed)

    @async_test
    async def test_connect_returns_when_exception_raised_after_close(self):
        client = SocketModeClient(
            app_token="xapp-A111-222-xyz",
            web_client=self.web_client,
            auto_reconnect_enabled=False,
            ping_interval=0.01,
        )
        client.logger = MagicMock()
        client.logger.level = logging.DEBUG

        async def close_then_raise(*args, **kwargs):
            await client.close()
            raise RuntimeError("Session is closed")

        client.issue_new_wss_url = close_then_raise

        await asyncio.wait_for(client.connect(), timeout=1.0)
        self.assertTrue(client.closed)
        client.logger.exception.assert_not_called()

    @async_test
    async def test_connect_recreates_closed_aiohttp_session(self):
        # Regression test for #1922: a closed aiohttp session made every reconnect attempt fail forever.
        client = SocketModeClient(
            app_token="xapp-A111-222-xyz",
            web_client=self.web_client,
            auto_reconnect_enabled=False,
            ping_interval=0.01,
        )
        client.wss_uri = "ws://localhost:8888/link"
        old_session = client.aiohttp_client_session
        await old_session.close()
        self.assertFalse(await client.is_connected())

        used_sessions = []

        async def ws_connect(session, *args, **kwargs):
            used_sessions.append((session, session.closed))
            await client.close()
            raise RuntimeError("stop connecting")

        with patch.object(aiohttp.ClientSession, "ws_connect", ws_connect):
            await asyncio.wait_for(client.connect(), timeout=1.0)

        self.assertEqual(len(used_sessions), 1)
        session, closed = used_sessions[0]
        self.assertIsNot(session, old_session)
        self.assertFalse(closed)
        self.assertIs(client.aiohttp_client_session, session)
        self.assertTrue(session.closed)  # closed again by client.close()

    @async_test
    async def test_connect_does_not_recreate_session_when_closed_during_reconnect(self):
        client = SocketModeClient(
            app_token="xapp-A111-222-xyz",
            web_client=self.web_client,
            auto_reconnect_enabled=False,
        )
        client.wss_uri = "ws://localhost:8888/link"
        old_session = client.aiohttp_client_session

        async def close_during_reconnect():
            client.closed = True
            await old_session.close()

        client.current_session = MagicMock()
        client.current_session.close = close_during_reconnect
        try:
            with patch.object(aiohttp, "ClientSession") as new_session:
                await asyncio.wait_for(client.connect(), timeout=1.0)
                new_session.assert_not_called()
            self.assertIs(client.aiohttp_client_session, old_session)
            self.assertTrue(old_session.closed)
        finally:
            await client.close()

    @async_test
    async def test_init_with_loop(self):
        client = SocketModeClient(
            app_token="xapp-A111-222-xyz",
            web_client=self.web_client,
            auto_reconnect_enabled=False,
            loop=asyncio.get_event_loop(),
        )
        try:
            self.assertIsNotNone(client)
        finally:
            await client.close()

    @async_test
    async def test_issue_new_wss_url(self):
        client = SocketModeClient(
            app_token="xapp-A111-222-xyz",
            web_client=self.web_client,
            auto_reconnect_enabled=False,
        )
        try:
            url = await client.issue_new_wss_url()
            self.assertTrue(url.startswith("ws://"))
        finally:
            await client.close()

    # TODO: valid test to connect
    # @async_test
    # async def test_connect_to_new_endpoint(self):
    #     client = SocketModeClient(
    #         app_token="xapp-A111-222-xyz",
    #         web_client=self.web_client,
    #         auto_reconnect_enabled=False,
    #     )
    #     try:
    #         await client.connect_to_new_endpoint()
    #     except Exception as e:
    #         pass
    #     finally:
    #         await client.close()

    @async_test
    async def test_enqueue_message(self):
        client = SocketModeClient(
            app_token="xapp-A111-222-xyz",
            web_client=self.web_client,
            auto_reconnect_enabled=False,
            trace_enabled=True,
            on_message_listeners=[lambda msg: None],
        )
        client.message_listeners.append(listener)
        try:
            await client.enqueue_message("hello")
            await client.process_message()

            await client.enqueue_message(
                """{"type":"hello","num_connections":1,"debug_info":{"host":"applink-111-222","build_number":10,"approximate_connection_time":18060},"connection_info":{"app_id":"A111"}}"""
            )
            await client.process_message()
        finally:
            await client.disconnect()
            await client.close()


async def listener(self, message, raw_message):
    pass
