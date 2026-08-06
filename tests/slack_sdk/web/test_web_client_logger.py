import logging
import unittest
from unittest.mock import patch

from slack_sdk import WebClient
from slack_sdk.web import base_client
from tests.helpers import create_copy
from tests.mock_web_api_server import cleanup_mock_web_api_server, setup_mock_web_api_server
from tests.slack_sdk.web.mock_web_api_handler import MockHandler


class TestWebClientLogger(unittest.TestCase):
    test_logger: logging.Logger

    def setUp(self):
        self.test_logger = logging.getLogger("test-logger")
        setup_mock_web_api_server(self, MockHandler)

    def tearDown(self):
        cleanup_mock_web_api_server(self)

    def test_logger_property_returns_default_logger(self):
        client = WebClient(base_url="http://localhost:8888", token="xoxb-api_test")
        self.assertEqual(client.logger.name, base_client.__name__)

    def test_logger_property_returns_custom_logger(self):
        client = WebClient(
            base_url="http://localhost:8888",
            token="xoxb-api_test",
            logger=self.test_logger,
        )
        self.assertEqual(client.logger, self.test_logger)

    def test_logger_property_has_no_setter(self):
        client = WebClient(
            base_url="http://localhost:8888",
            token="xoxb-api_test",
        )
        with self.assertRaises(AttributeError):
            client.logger = self.test_logger

    def test_ensure_web_client_with_logger_is_copyable(self):
        with patch("slack_sdk.web.base_client.create_ssl_context_with_certifi_fallback", return_value=None):
            client = WebClient(
                base_url="http://localhost:8888",
                token="xoxb-api_test",
                logger=self.test_logger,
            )
            client_copy = create_copy(client)
            self.assertEqual(client.logger, self.test_logger)
            self.assertEqual(client_copy.logger, self.test_logger)
