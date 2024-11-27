from unittest import TestCase

from slack_sdk.web import WebClient
from tests.slack_sdk.web.mock_web_api_handler import MockHandler
from tests.mock_web_api_server import setup_mock_web_api_server, cleanup_mock_web_api_server, assert_received_request_count


class TestWebClientUrlFormat(TestCase):
    def setUp(self):
        setup_mock_web_api_server(self, MockHandler)
        self.client = WebClient(token="xoxb-api_test", base_url="http://localhost:8888")
        self.client_base_url_slash = WebClient(token="xoxb-api_test", base_url="http://localhost:8888/")

    def tearDown(self):
        cleanup_mock_web_api_server(self)

    def test_base_url_without_slash_api_method_without_slash(self):
        self.client.api_call("chat.postMessage")
        assert_received_request_count(self, "/chat.postMessage", 1)

    def test_base_url_without_slash_api_method_with_slash(self):
        self.client.api_call("/chat.postMessage")
        assert_received_request_count(self, "/chat.postMessage", 1)

    def test_base_url_with_slash_api_method_without_slash(self):
        self.client_base_url_slash.api_call("chat.postMessage")
        assert_received_request_count(self, "/chat.postMessage", 1)

    def test_base_url_with_slash_api_method_with_slash(self):
        self.client_base_url_slash.api_call("/chat.postMessage")
        assert_received_request_count(self, "/chat.postMessage", 1)

    def test_base_url_without_slash_api_method_with_slash_and_trailing_slash(self):
        self.client.api_call("/chat.postMessage/")
        assert_received_request_count(self, "/chat.postMessage/", 1)
