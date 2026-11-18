import unittest

from slack_sdk.audit_logs.async_client import AsyncAuditLogsClient
from slack_sdk.http_retry.builtin_async_handlers import AsyncRateLimitErrorRetryHandler, AsyncServerErrorRetryHandler
from tests.helpers import async_test
from tests.slack_sdk.audit_logs.mock_web_api_handler import MockHandler
from tests.mock_web_api_server import (
    assert_received_request_count_async,
    cleanup_mock_web_api_server_async,
    setup_mock_web_api_server_async,
)
from ..my_retry_handler import MyRetryHandler


class TestAsyncAuditLogsClient_HttpRetries(unittest.TestCase):
    def setUp(self):
        setup_mock_web_api_server_async(self, MockHandler)

    def tearDown(self):
        cleanup_mock_web_api_server_async(self)

    @async_test
    async def test_http_retries(self):
        retry_handler = MyRetryHandler(max_retry_count=2)
        client = AsyncAuditLogsClient(
            token="xoxp-remote_disconnected",
            base_url="http://localhost:8888/",
            retry_handlers=[retry_handler],
        )
        try:
            await client.actions()
            self.fail("An exception is expected")
        except Exception as _:
            pass

        self.assertEqual(2, retry_handler.call_count)

    @async_test
    async def test_ratelimited(self):
        client = AsyncAuditLogsClient(
            token="xoxp-ratelimited",
            base_url="http://localhost:8888/",
            retry_handlers=[AsyncRateLimitErrorRetryHandler()],
        )

        response = await client.actions()
        # Just running retries; no assertions for call count so far
        self.assertEqual(429, response.status_code)

    @async_test
    async def test_server_error(self):
        client = AsyncAuditLogsClient(
            token="xoxp-",
            base_url="http://localhost:8888/",
            retry_handlers=[AsyncServerErrorRetryHandler(max_retry_count=1)],
        )

        response = await client.api_call(path="error")
        self.assertEqual(500, response.status_code)
        await assert_received_request_count_async(self, "/error", 2)
