import unittest

from slack_sdk.errors import SlackApiError
from slack_sdk.http_retry import RateLimitErrorRetryHandler
from slack_sdk.web import WebClient
from tests.slack_sdk.web.mock_web_api_server import (
    cleanup_mock_web_api_server,
    setup_mock_web_api_server,
)
from ..fatal_error_retry_handler import FatalErrorRetryHandler
from ..my_retry_handler import MyRetryHandler


class TestWebClient_HttpRetry(unittest.TestCase):
    def setUp(self):
        setup_mock_web_api_server(self)

    def tearDown(self):
        cleanup_mock_web_api_server(self)

    def test_remote_disconnected(self):
        retry_handler = MyRetryHandler(max_retry_count=2)
        client = WebClient(
            base_url="http://localhost:8888",
            token="xoxb-remote_disconnected",
            team_id="T111",
            retry_handlers=[retry_handler],
        )
        try:
            client.auth_test()
            self.fail("An exception is expected")
        except Exception as _:
            pass

        self.assertEqual(2, retry_handler.call_count)

    def test_ratelimited_no_retry(self):
        client = WebClient(
            base_url="http://localhost:8888",
            token="xoxb-ratelimited",
            team_id="T111",
        )
        try:
            client.auth_test()
            self.fail("An exception is expected")
        except SlackApiError as e:
            # Just running retries; no assertions for call count so far
            self.assertEqual(429, e.response.status_code)

    def test_ratelimited(self):
        client = WebClient(
            base_url="http://localhost:8888",
            token="xoxb-ratelimited_only_once",
            team_id="T111",
        )
        client.retry_handlers.append(RateLimitErrorRetryHandler())
        # The auto-retry should work here
        client.auth_test()

    def test_fatal_error_no_retry(self):
        client = WebClient(
            base_url="http://localhost:8888",
            token="xoxb-fatal_error",
            team_id="T111",
        )
        try:
            client.auth_test()
            self.fail("An exception is expected")
        except SlackApiError as e:
            # Just running retries; no assertions for call count so far
            self.assertEqual(200, e.response.status_code)
            self.assertEqual("fatal_error", e.response["error"])

    def test_fatal_error(self):
        client = WebClient(
            base_url="http://localhost:8888",
            token="xoxb-fatal_error_only_once",
            team_id="T111",
        )
        client.retry_handlers.append(FatalErrorRetryHandler())
        # The auto-retry should work here
        client.auth_test()
