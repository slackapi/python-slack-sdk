import unittest

from aiohttp import ServerDisconnectedError
from slack_sdk.audit_logs.async_client import AsyncAuditLogsClient
from tests.helpers import async_test
from tests.slack_sdk.audit_logs.mock_web_api_server import (
    cleanup_mock_web_api_server,
    setup_mock_web_api_server,
)
from ..my_retry_handler import MyRetryHandler


class TestAsyncAuditLogsClient_HttpRetries(unittest.TestCase):
    def setUp(self):
        setup_mock_web_api_server(self)

    def tearDown(self):
        cleanup_mock_web_api_server(self)

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
        except ServerDisconnectedError as _:
            pass

        self.assertEqual(2, retry_handler.call_count)
