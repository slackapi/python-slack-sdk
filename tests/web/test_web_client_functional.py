import unittest

import slack
from tests.web.mock_web_api_server import (
    setup_mock_web_api_server,
    cleanup_mock_web_api_server,
)


class TestWebClientFunctional(unittest.TestCase):
    def setUp(self):
        setup_mock_web_api_server(self)
        self.client = slack.WebClient(token="xoxb-api_test", base_url="http://localhost:8888")

    def tearDown(self):
        cleanup_mock_web_api_server(self)

    def test_requests_with_use_session_turned_off(self):
        self.client.use_pooling = False
        resp = self.client.api_test()
        assert resp["ok"]

    def test_subsequent_requests_with_a_session_succeeds(self):
        resp = self.client.api_test()
        assert resp["ok"]
        resp = self.client.api_test()
        assert resp["ok"]
