import json
import unittest

from slack_sdk.http_retry.builtin_async_handlers import AsyncRateLimitErrorRetryHandler, AsyncServerErrorRetryHandler
from slack_sdk.scim.v1.async_client import AsyncSCIMClient
from tests.helpers import async_test
from tests.slack_sdk.scim.mock_web_api_handler import MockHandler
from tests.mock_web_api_server import (
    assert_received_request_count_async,
    cleanup_mock_web_api_server_async,
    setup_mock_web_api_server_async,
)
from ..my_retry_handler import MyRetryHandler
from ..rate_limited_retry_handler import RateLimitedRetryHandler
from ..error_recording_retry_handler import ErrorRecordingRetryHandler, error_statuses


class TestSCIMClient_HttpRetries(unittest.TestCase):
    def setUp(self):
        setup_mock_web_api_server_async(self, MockHandler)

    def tearDown(self):
        cleanup_mock_web_api_server_async(self)

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

    @async_test
    async def test_server_error(self):
        client = AsyncSCIMClient(
            base_url="http://localhost:8888/",
            token="xoxp-server_error",
            retry_handlers=[AsyncServerErrorRetryHandler(max_retry_count=1)],
        )

        response = await client.api_call(http_verb="GET", path="Users")
        self.assertEqual(500, response.status_code)
        await assert_received_request_count_async(self, "/Users", 2)

    @async_test
    async def test_server_error_passes_the_status_error_to_handlers(self):
        retry_handler = ErrorRecordingRetryHandler()
        client = AsyncSCIMClient(
            base_url="http://localhost:8888/",
            token="xoxp-server_error",
            retry_handlers=[retry_handler],
        )

        await client.api_call(http_verb="GET", path="Users")

        self.assertEqual([500], error_statuses(retry_handler.can_retry_errors))
        self.assertEqual([500], error_statuses(retry_handler.prepare_errors))

    @async_test
    async def test_ratelimited_returns_the_last_response_when_retries_run_out(self):
        retry_handler = RateLimitedRetryHandler(max_retry_count=100)
        client = AsyncSCIMClient(
            base_url="http://localhost:8888/",
            token="xoxp-ratelimited",
            retry_handlers=[retry_handler],
        )

        response = await client.search_users(start_index=0, count=1)

        self.assertEqual(429, response.status_code)
        self.assertEqual(100, retry_handler.retry_count)

    @async_test
    async def test_ratelimited_retries_a_malformed_body_without_parsing_it(self):
        client = AsyncSCIMClient(
            base_url="http://localhost:8888/",
            token="xoxp-ratelimited_malformed",
            retry_handlers=[RateLimitedRetryHandler(max_retry_count=2)],
        )

        with self.assertRaises(json.JSONDecodeError):
            await client.api_call(http_verb="GET", path="Users")

        await assert_received_request_count_async(self, "/Users", 3)
