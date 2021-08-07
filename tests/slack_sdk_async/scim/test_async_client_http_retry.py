import unittest

from slack_sdk.http_retry.builtin_async_handlers import AsyncRateLimitErrorRetryHandler
from slack_sdk.scim.v1.async_client import AsyncSCIMClient
from tests.helpers import async_test
from tests.slack_sdk.scim.mock_web_api_server import (
    setup_mock_web_api_server,
    cleanup_mock_web_api_server,
)
from ..my_retry_handler import MyRetryHandler


class TestSCIMClient_HttpRetries(unittest.TestCase):
    def setUp(self):
        setup_mock_web_api_server(self)

    def tearDown(self):
        cleanup_mock_web_api_server(self)

    @async_test
    async def test_retries(self):
        retry_handler = MyRetryHandler(max_retry_count=2)
        client = AsyncSCIMClient(
            base_url="http://localhost:8888/",
            token="xoxp-remote_disconnected",
            retry_handlers=[retry_handler],
        )

        try:
            await client.search_users(start_index=0, count=1)
            self.fail("An exception is expected")
        except Exception as _:
            pass

        self.assertEqual(2, retry_handler.call_count)

    @async_test
    async def test_ratelimited(self):
        client = AsyncSCIMClient(
            base_url="http://localhost:8888/",
            token="xoxp-ratelimited",
            retry_handlers=[AsyncRateLimitErrorRetryHandler()],
        )

        response = await client.search_users(start_index=0, count=1)
        # Just running retries; no assertions for call count so far
        self.assertEqual(429, response.status_code)
