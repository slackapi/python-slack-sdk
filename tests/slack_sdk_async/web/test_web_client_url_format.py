import unittest
from unittest.mock import Mock
from aiohttp import ClientSession

from slack_sdk.web.async_client import AsyncWebClient
from tests.slack_sdk_async.helpers import async_test
from tests.slack_sdk.web.mock_web_api_server import (
    setup_mock_web_api_server,
    cleanup_mock_web_api_server,
)


class TestAsyncWebClientUrlFormat(unittest.TestCase):
    def setUp(self):
        setup_mock_web_api_server(self)

        self.session = ClientSession()

        def spy_session_request(*args, **kwargs):
            self.session_request_spy_args = args
            self.session_request_spy_kwargs = kwargs
            return self.session.request(*args, **kwargs)

        self.spy_session = ClientSession()
        self.spy_session.request = Mock(side_effect=spy_session_request)
        self.client = AsyncWebClient(token="xoxb-api_test", base_url="http://localhost:8888", session=self.spy_session)
        self.client_base_url_slash = AsyncWebClient(
            token="xoxb-api_test", base_url="http://localhost:8888/", session=self.spy_session
        )

    def tearDown(self):
        cleanup_mock_web_api_server(self)

    async def close_sessions(self):
        await self.session.close()
        await self.spy_session.close()

    @async_test
    async def test_base_url_without_slash_api_method_without_slash(self):
        await self.client.api_call("api.test")
        await self.close_sessions()
        self.assertIsInstance(self.session_request_spy_args[1], str)
        self.assertEqual(self.session_request_spy_args[1], "http://localhost:8888/api.test")

    @async_test
    async def test_base_url_without_slash_api_method_with_slash(self):
        await self.client.api_call("/api.test")
        await self.close_sessions()
        self.assertIsInstance(self.session_request_spy_args[1], str)
        self.assertEqual(self.session_request_spy_args[1], "http://localhost:8888/api.test")

    @async_test
    async def test_base_url_with_slash_api_method_without_slash(self):
        await self.client_base_url_slash.api_call("api.test")
        await self.close_sessions()
        self.assertIsInstance(self.session_request_spy_args[1], str)
        self.assertEqual(self.session_request_spy_args[1], "http://localhost:8888/api.test")

    @async_test
    async def test_base_url_with_slash_api_method_with_slash(self):
        await self.client_base_url_slash.api_call("/api.test")
        await self.close_sessions()
        self.assertIsInstance(self.session_request_spy_args[1], str)
        self.assertEqual(self.session_request_spy_args[1], "http://localhost:8888/api.test")

    @async_test
    async def test_base_url_without_slash_api_method_with_slash_and_trailing_slash(self):
        await self.client.api_call("/api.test/")
        await self.close_sessions()
        self.assertIsInstance(self.session_request_spy_args[1], str)
        self.assertEqual(self.session_request_spy_args[1], "http://localhost:8888/api.test/")
