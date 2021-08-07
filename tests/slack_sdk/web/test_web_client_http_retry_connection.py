import unittest

from slack_sdk.web import WebClient
from tests.slack_sdk.web.mock_web_api_server_http_retry import (
    setup_mock_retry_web_api_server,
    cleanup_mock_retry_web_api_server,
)


class TestWebClient_HttpRetry(unittest.TestCase):
    def setUp(self):
        setup_mock_retry_web_api_server(self)

    def tearDown(self):
        cleanup_mock_retry_web_api_server(self)

    def test_remote_disconnected(self):
        client = WebClient(
            base_url="http://localhost:8889",
            token="xoxb-remote_disconnected",
            team_id="T111",
        )
        client.auth_test()
