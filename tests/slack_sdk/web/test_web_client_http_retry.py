import unittest

from slack_sdk.web import WebClient
from tests.slack_sdk.web.mock_web_api_server import (
    cleanup_mock_web_api_server,
    setup_mock_web_api_server,
)
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
