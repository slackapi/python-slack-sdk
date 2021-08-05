import unittest

from slack_sdk.web.async_client import AsyncWebClient
from tests.slack_sdk_async.helpers import async_test
from tests.slack_sdk.web.mock_web_api_server import (
    setup_mock_web_api_server,
    cleanup_mock_web_api_server,
)
from ..my_retry_handler import MyRetryHandler


class TestAsyncWebClient_HttpRetries(unittest.TestCase):
    def setUp(self):
        setup_mock_web_api_server(self)

    def tearDown(self):
        cleanup_mock_web_api_server(self)

    @async_test
    async def test_retries(self):
        retry_handler = MyRetryHandler(max_retry_count=2)
        client = AsyncWebClient(
            token="xoxp-remote_disconnected",
            base_url="http://localhost:8888",
            retry_handlers=[retry_handler],
        )
        try:
            await client.auth_test()
            self.fail("An exception is expected")
        except Exception as _:
            pass

        self.assertEqual(2, retry_handler.call_count)
