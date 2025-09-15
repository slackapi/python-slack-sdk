import logging
import unittest

from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.web import async_base_client
from tests.helpers import create_copy
from tests.slack_sdk.web.mock_web_api_handler import MockHandler
from tests.mock_web_api_server import setup_mock_web_api_server_async, cleanup_mock_web_api_server_async


class TestAsyncWebClientLogger(unittest.TestCase):
    test_logger: logging.Logger

    def setUp(self):
        self.test_logger = logging.getLogger("test-logger")
        setup_mock_web_api_server_async(self, MockHandler)

    def tearDown(self):
        cleanup_mock_web_api_server_async(self)

    def test_logger_property_returns_default_logger(self):
        client = AsyncWebClient(base_url="http://localhost:8888", token="xoxb-api_test")
        self.assertEqual(client.logger.name, async_base_client.__name__)

    def test_logger_property_returns_custom_logger(self):
        client = AsyncWebClient(
            base_url="http://localhost:8888",
            token="xoxb-api_test",
            logger=self.test_logger,
        )
        self.assertEqual(client.logger, self.test_logger)

    def test_logger_property_has_no_setter(self):
        client = AsyncWebClient(
            base_url="http://localhost:8888",
            token="xoxb-api_test",
        )
        with self.assertRaises(AttributeError):
            client.logger = self.test_logger

    def test_ensure_async_web_client_with_logger_is_copyable(self):
        client = AsyncWebClient(
            base_url="http://localhost:8888",
            token="xoxb-api_test",
            logger=self.test_logger,
        )
        client_copy = create_copy(client)
        self.assertEqual(client.logger, self.test_logger)
        self.assertEqual(client_copy.logger, self.test_logger)
