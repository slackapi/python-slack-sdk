import logging
import unittest

from slack_sdk import WebClient
from slack_sdk.web import base_client
from tests.slack_sdk.web.mock_web_api_handler import MockHandler
from tests.mock_web_api_server import setup_mock_web_api_server, cleanup_mock_web_api_server


class TestWebClientLogger(unittest.TestCase):
    test_logger: logging.Logger

    def setUp(self):
        self.test_logger = logging.Logger("test-logger")
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
