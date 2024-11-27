import unittest

from slack_sdk.web import WebClient
from tests.slack_sdk.web.mock_web_api_http_retry_handler import MockHandler
from tests.mock_web_api_server import setup_mock_web_api_server, cleanup_mock_web_api_server


class TestWebClient_HttpRetry(unittest.TestCase):
    def setUp(self):
        setup_mock_web_api_server(self, MockHandler, port=8889)

    def tearDown(self):
        cleanup_mock_web_api_server(self)

    def test_remote_disconnected(self):
        client = WebClient(
            base_url="http://localhost:8889",
            token="xoxb-remote_disconnected",
            team_id="T111",
        )
        client.auth_test()
