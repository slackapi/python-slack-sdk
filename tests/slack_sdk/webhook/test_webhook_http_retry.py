import unittest

from slack_sdk.http_retry import RateLimitErrorRetryHandler
from slack_sdk.webhook import WebhookClient
from tests.slack_sdk.webhook.mock_web_api_server import (
    cleanup_mock_web_api_server,
    setup_mock_web_api_server,
)
from ..my_retry_handler import MyRetryHandler


class TestWebhook_HttpRetries(unittest.TestCase):
    def setUp(self):
        setup_mock_web_api_server(self)

    def tearDown(self):
        cleanup_mock_web_api_server(self)

    def test_send(self):
        retry_handler = MyRetryHandler(max_retry_count=2)
        client = WebhookClient(
            "http://localhost:8888/remote_disconnected",
            retry_handlers=[retry_handler],
        )
        try:
            client.send(text="hello!")
            self.fail("An exception is expected")
        except Exception as _:
            pass

        self.assertEqual(2, retry_handler.call_count)

    def test_ratelimited(self):
        client = WebhookClient("http://localhost:8888/ratelimited")
        client.retry_handlers.append(RateLimitErrorRetryHandler())
        response = client.send(text="hello!")
        # Just running retries; no assertions for call count so far
        self.assertEqual(429, response.status_code)
