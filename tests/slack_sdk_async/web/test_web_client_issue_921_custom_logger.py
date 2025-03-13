import unittest
from logging import Logger

from slack_sdk.web.async_client import AsyncWebClient
from tests.helpers import async_test
from tests.slack_sdk.web.mock_web_api_handler import MockHandler
from tests.mock_web_api_server import setup_mock_web_api_server_async, cleanup_mock_web_api_server_async


class TestWebClient_Issue_921_CustomLogger(unittest.TestCase):
    def setUp(self):
        setup_mock_web_api_server_async(self, MockHandler)

    def tearDown(self):
        cleanup_mock_web_api_server_async(self)

    @async_test
    async def test_if_it_uses_custom_logger(self):
        logger = CustomLogger("test-logger")
        client = AsyncWebClient(
            base_url="http://localhost:8888",
            token="xoxb-api_test",
            logger=logger,
        )
        await client.chat_postMessage(channel="C111", text="hello")
        self.assertTrue(logger.called)

    def test_if_property_returns_custom_logger(self):
        logger = CustomLogger("test-logger")
        client = AsyncWebClient(
            base_url="http://localhost:8888",
            token="xoxb-api_test",
            logger=logger,
        )
        self.assertEqual(client.logger, logger)

    def test_logger_property_has_no_setter(self):
        client = AsyncWebClient(
            base_url="http://localhost:8888",
            token="xoxb-api_test",
        )
        with self.assertRaises(AttributeError):
            client.logger = CustomLogger("test-logger")


class CustomLogger(Logger):
    called: bool

    def __init__(self, name, level="DEBUG"):
        Logger.__init__(self, name, level)
        self.called = False

    def debug(self, msg, *args, **kwargs):
        self.called = True
