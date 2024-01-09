import unittest

from slack_sdk.socket_mode.websockets import SocketModeClient
from slack_sdk.web.async_client import AsyncWebClient
from tests.slack_sdk.socket_mode.mock_web_api_server import (
    setup_mock_web_api_server,
    cleanup_mock_web_api_server,
)
from tests.slack_sdk_async.helpers import async_test


class TestAiohttp(unittest.TestCase):
    def setUp(self):
        setup_mock_web_api_server(self)
        self.web_client = AsyncWebClient(
            token="xoxb-api_test",
            base_url="http://localhost:8888",
        )

    def tearDown(self):
        cleanup_mock_web_api_server(self)

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


async def listener(message, raw_message):
    pass
