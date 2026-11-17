import asyncio
import unittest
from unittest.mock import MagicMock

from websockets.exceptions import WebSocketException

from slack_sdk.socket_mode.websockets import SocketModeClient
from slack_sdk.web.async_client import AsyncWebClient
from tests.slack_sdk.socket_mode.mock_web_api_handler import MockHandler
from tests.mock_web_api_server import setup_mock_web_api_server_async, cleanup_mock_web_api_server_async
from tests.slack_sdk_async.helpers import async_test


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
        client = SocketModeClient(app_token="xapp-A111-222-xyz")
        try:
            self.assertIsNotNone(client)
        finally:
            await client.close()

    @async_test
    async def test_issue_new_wss_url(self):
        client = SocketModeClient(
            app_token="xapp-A111-222-xyz",
            web_client=self.web_client,
        )
        try:
            url = await client.issue_new_wss_url()
            self.assertTrue(url.startswith("ws://"))
        finally:
            await client.close()

    @async_test
    async def test_connect_to_new_endpoint(self):
        client = SocketModeClient(
            app_token="xapp-A111-222-xyz",
            web_client=self.web_client,
        )
        try:
            await client.connect_to_new_endpoint()
        except Exception as e:
            # TODO: valida test to connect
            pass
        finally:
            await client.close()

    @async_test
    async def test_enqueue_message(self):
        client = SocketModeClient(
            app_token="xapp-A111-222-xyz",
            web_client=self.web_client,
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
            await client.close()

    @async_test
    async def test_send_message_leaves_a_lock_held_by_another_task(self):
        client = SocketModeClient(
            app_token="xapp-A111-222-xyz",
            web_client=self.web_client,
        )

        async def send(message):
            raise WebSocketException("the connection was replaced")

        client.current_session = MagicMock()
        client.current_session.send = send
        await client.connect_operation_lock.acquire()
        try:
            with self.assertRaises(asyncio.TimeoutError):
                await asyncio.wait_for(client.send_message("hello"), timeout=0.1)
            self.assertTrue(client.connect_operation_lock.locked())
        finally:
            if client.connect_operation_lock.locked():
                client.connect_operation_lock.release()
            client.current_session = None
            await client.close()


async def listener(message, raw_message):
    pass
