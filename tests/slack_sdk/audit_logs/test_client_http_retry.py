import unittest

from slack_sdk.audit_logs import AuditLogsClient
from slack_sdk.http_retry import RateLimitErrorRetryHandler
from tests.slack_sdk.audit_logs.mock_web_api_server import (
    cleanup_mock_web_api_server,
    setup_mock_web_api_server,
)
from ..my_retry_handler import MyRetryHandler


class TestAuditLogsClient_HttpRetries(unittest.TestCase):
    def setUp(self):
        setup_mock_web_api_server(self)

    def tearDown(self):
        cleanup_mock_web_api_server(self)

    def test_retries(self):
        retry_handler = MyRetryHandler(max_retry_count=2)
        client = AuditLogsClient(
            token="xoxp-remote_disconnected",
            base_url="http://localhost:8888/",
            retry_handlers=[retry_handler],
        )
        try:
            client.actions()
            self.fail("An exception is expected")
        except Exception as _:
            pass

        self.assertEqual(2, retry_handler.call_count)

    def test_ratelimited(self):
        client = AuditLogsClient(
            token="xoxp-ratelimited",
            base_url="http://localhost:8888/",
        )
        client.retry_handlers.append(RateLimitErrorRetryHandler())

        response = client.actions()
        # Just running retries; no assertions for call count so far
        self.assertEqual(429, response.status_code)
