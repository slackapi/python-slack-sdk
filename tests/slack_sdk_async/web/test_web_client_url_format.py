import unittest

from slack_sdk.web.async_client import AsyncWebClient
from tests.slack_sdk_async.helpers import async_test
from tests.slack_sdk.web.mock_web_api_handler import MockHandler
from tests.mock_web_api_server import (
    setup_mock_web_api_server_async,
    cleanup_mock_web_api_server_async,
    assert_received_request_count_async,
)


class TestAsyncWebClientUrlFormat(unittest.TestCase):
    def setUp(self):
        setup_mock_web_api_server_async(self, MockHandler)
        self.client = AsyncWebClient(token="xoxb-api_test", base_url="http://localhost:8888")
        self.client_base_url_slash = AsyncWebClient(token="xoxb-api_test", base_url="http://localhost:8888/")
        self.client_api = AsyncWebClient(token="xoxb-api_test", base_url="http://localhost:8888/api")
        self.client_api_slash = AsyncWebClient(token="xoxb-api_test", base_url="http://localhost:8888/api/")

    def tearDown(self):
        cleanup_mock_web_api_server_async(self)

    @async_test
    async def test_base_url_without_slash_api_method_without_slash(self):
        await self.client.api_call("chat.postMessage")
        await assert_received_request_count_async(self, "/chat.postMessage", 1)

    @async_test
    async def test_base_url_without_slash_api_method_with_slash(self):
        await self.client.api_call("/chat.postMessage")
        await assert_received_request_count_async(self, "/chat.postMessage", 1)

    @async_test
    async def test_base_url_with_slash_api_method_without_slash(self):
        await self.client_base_url_slash.api_call("chat.postMessage")
        await assert_received_request_count_async(self, "/chat.postMessage", 1)

    @async_test
    async def test_base_url_with_slash_api_method_with_slash(self):
        await self.client_base_url_slash.api_call("/chat.postMessage")
        await assert_received_request_count_async(self, "/chat.postMessage", 1)

    @async_test
    async def test_base_url_without_slash_api_method_with_slash_and_trailing_slash(self):
        await self.client.api_call("/chat.postMessage/")
        await assert_received_request_count_async(self, "/chat.postMessage/", 1)

    @async_test
    async def test_base_url_with_api(self):
        await self.client_api.api_call("chat.postMessage")
        assert_received_request_count_async(self, "/api/chat.postMessage", 1)

    @async_test
    async def test_base_url_with_api_method_without_slash_method_with_slash(self):
        await self.client_api.api_call("/chat.postMessage")
        assert_received_request_count_async(self, "/api/chat.postMessage", 1)

    @async_test
    async def test_base_url_with_api_slash(self):
        await self.client_api_slash.api_call("chat.postMessage")
        await assert_received_request_count_async(self, "/api/chat.postMessage", 1)

    @async_test
    async def test_base_url_with_api_slash_and_method_with_slash(self):
        await self.client_api_slash.api_call("/chat.postMessage")
        await assert_received_request_count_async(self, "/api/chat.postMessage", 1)
