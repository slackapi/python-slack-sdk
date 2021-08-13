import unittest

from slack_sdk.http_retry import RateLimitErrorRetryHandler
from slack_sdk.scim import SCIMClient
from tests.slack_sdk.scim.mock_web_api_server import (
    setup_mock_web_api_server,
    cleanup_mock_web_api_server,
)
from ..my_retry_handler import MyRetryHandler


class TestSCIMClient(unittest.TestCase):
    def setUp(self):
        setup_mock_web_api_server(self)

    def tearDown(self):
        cleanup_mock_web_api_server(self)

    def test_retries(self):
        retry_handler = MyRetryHandler(max_retry_count=2)
        client = SCIMClient(
            base_url="http://localhost:8888/",
            token="xoxp-remote_disconnected",
            retry_handlers=[retry_handler],
        )

        try:
            client.search_users(start_index=0, count=1)
            self.fail("An exception is expected")
        except Exception as _:
            pass

        self.assertEqual(2, retry_handler.call_count)

    def test_ratelimited(self):
        client = SCIMClient(
            base_url="http://localhost:8888/",
            token="xoxp-ratelimited",
        )
        client.retry_handlers.append(RateLimitErrorRetryHandler())

        response = client.search_users(start_index=0, count=1)
        # Just running retries; no assertions for call count so far
        self.assertEqual(429, response.status_code)
