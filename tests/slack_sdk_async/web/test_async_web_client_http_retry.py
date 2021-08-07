import unittest

import slack_sdk.errors as err
from slack_sdk.http_retry.builtin_async_handlers import AsyncRateLimitErrorRetryHandler
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
    async def test_api_calls_return_a_future(self):
        pass

    @async_test
    async def test_remote_disconnected(self):
        retry_handler = MyRetryHandler(max_retry_count=2)
        client = AsyncWebClient(
            base_url="http://localhost:8888",
            token="xoxp-remote_disconnected",
            team_id="T111",
            retry_handlers=[retry_handler],
        )
        try:
            await client.auth_test()
            self.fail("An exception is expected")
        except Exception as _:
            pass

        self.assertEqual(2, retry_handler.call_count)

    @async_test
    async def test_ratelimited(self):
        client = AsyncWebClient(
            base_url="http://localhost:8888",
            token="xoxp-ratelimited",
            team_id="T111",
            retry_handlers=[AsyncRateLimitErrorRetryHandler()],
        )
        try:
            await client.auth_test()
            self.fail("An exception is expected")
        except err.SlackApiError as e:
            # Just running retries; no assertions for call count so far
            self.assertEqual(429, e.response.status_code)
