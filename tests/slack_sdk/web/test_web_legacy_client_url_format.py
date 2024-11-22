from unittest import TestCase
from unittest.mock import patch
from urllib import request
from urllib.request import Request, urlopen

import slack_sdk.web.legacy_base_client
from tests.helpers import reload_module
from tests.slack_sdk.web.mock_web_api_server import (
    setup_mock_web_api_server,
    cleanup_mock_web_api_server,
)


def build_spy_urlopen(test: TestCase):
    def spy_urlopen(*args, **kwargs):
        test.urlopen_spy_args = args
        test.urlopen_spy_kwargs = kwargs
        return urlopen(*args, **kwargs)

    return spy_urlopen


class TestLegacyWebClientUrlFormat(TestCase):
    def setUp(self):
        setup_mock_web_api_server(self)
        with patch.object(request, "urlopen") as mock_urlopen:
            mock_urlopen.side_effect = build_spy_urlopen(self)
            reload_module(slack_sdk.web.legacy_base_client)
        self.client = slack_sdk.web.legacy_base_client.LegacyBaseClient(
            token="xoxb-api_test", base_url="http://localhost:8888"
        )
        self.client_base_url_slash = slack_sdk.web.legacy_base_client.LegacyBaseClient(
            token="xoxb-api_test", base_url="http://localhost:8888/"
        )

    def tearDown(self):
        cleanup_mock_web_api_server(self)
        self.urlopen_spy_args = None
        self.urlopen_spy_kwargs = None

    @classmethod
    def tearDownClass(cls):
        reload_module(slack_sdk.web.legacy_base_client)

    def test_base_url_without_slash_api_method_without_slash(self):
        self.client.api_call("api.test")
        self.assertIsInstance(self.urlopen_spy_args[0], Request)
        self.assertEqual(self.urlopen_spy_args[0].full_url, "http://localhost:8888/api.test")

    def test_base_url_without_slash_api_method_with_slash(self):
        self.client.api_call("/api.test")
        self.assertIsInstance(self.urlopen_spy_args[0], Request)
        self.assertEqual(self.urlopen_spy_args[0].full_url, "http://localhost:8888/api.test")

    def test_base_url_with_slash_api_method_without_slash(self):
        self.client_base_url_slash.api_call("api.test")
        self.assertIsInstance(self.urlopen_spy_args[0], Request)
        self.assertEqual(self.urlopen_spy_args[0].full_url, "http://localhost:8888/api.test")

    def test_base_url_with_slash_api_method_with_slash(self):
        self.client_base_url_slash.api_call("/api.test")
        self.assertIsInstance(self.urlopen_spy_args[0], Request)
        self.assertEqual(self.urlopen_spy_args[0].full_url, "http://localhost:8888/api.test")

    def test_base_url_without_slash_api_method_with_slash_and_trailing_slash(self):
        self.client.api_call("/api.test/")
        self.assertIsInstance(self.urlopen_spy_args[0], Request)
        self.assertEqual(self.urlopen_spy_args[0].full_url, "http://localhost:8888/api.test/")
