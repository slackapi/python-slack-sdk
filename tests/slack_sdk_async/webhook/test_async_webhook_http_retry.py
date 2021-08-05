import unittest
from aiohttp import ClientOSError
from slack_sdk.webhook.async_client import AsyncWebhookClient
from tests.slack_sdk_async.helpers import async_test
from tests.slack_sdk.webhook.mock_web_api_server import (
    cleanup_mock_web_api_server,
    setup_mock_web_api_server,
)
from ..my_retry_handler import MyRetryHandler


class TestAsyncWebhook_HttpRetries(unittest.TestCase):
    def setUp(self):
        setup_mock_web_api_server(self)

    def tearDown(self):
        cleanup_mock_web_api_server(self)

    @async_test
    async def test_send(self):
        retry_handler = MyRetryHandler(max_retry_count=2)
        client = AsyncWebhookClient(
            "http://localhost:8888/remote_disconnected",
            retry_handlers=[retry_handler],
        )
        try:
            await client.send(text="hello!")
            self.fail("An exception is expected")
        except ClientOSError as _:
            pass

        self.assertEqual(2, retry_handler.call_count)
