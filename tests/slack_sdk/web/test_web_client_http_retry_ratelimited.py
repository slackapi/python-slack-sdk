import unittest

from slack_sdk.web import WebClient
from tests.slack_sdk.web.mock_web_api_server import (
    setup_mock_web_api_server,
    cleanup_mock_web_api_server,
)
from slack_sdk.http_retry import rate_limit_error_retry_handler


class TestWebClient_HttpRetry_RateLimited(unittest.TestCase):
    def setUp(self):
        setup_mock_web_api_server(self)

    def tearDown(self):
        cleanup_mock_web_api_server(self)

    def test_rate_limited(self):
        client = WebClient(
            base_url="http://localhost:8888",
            token="xoxb-rate_limited_only_once",
            team_id="T111",
            retry_handlers=[rate_limit_error_retry_handler],
        )
        client.auth_test()
