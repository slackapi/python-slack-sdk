import unittest
from logging import Logger

from slack_sdk.web.async_client import AsyncWebClient
from tests.helpers import async_test
from tests.slack_sdk.web.mock_web_api_server import (
    setup_mock_web_api_server,
    cleanup_mock_web_api_server,
)


class TestWebClient_Issue_921_CustomLogger(unittest.TestCase):
    def setUp(self):
        setup_mock_web_api_server(self)

    def tearDown(self):
        cleanup_mock_web_api_server(self)

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


class CustomLogger(Logger):
    called: bool

    def __init__(self, name, level="DEBUG"):
        Logger.__init__(self, name, level)
        self.called = False

    def debug(self, msg, *args, **kwargs):
        self.called = True
