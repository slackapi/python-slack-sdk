import asyncio
import os
import unittest
from urllib.error import URLError

from aiohttp import ClientConnectorError

from integration_tests.env_variable_names import SLACK_SDK_TEST_BOT_TOKEN
from integration_tests.helpers import async_test
from slack import WebClient


class TestWebClient(unittest.TestCase):

    def setUp(self):
        self.proxy = "http://invalid-host:9999"
        self.bot_token = os.environ[SLACK_SDK_TEST_BOT_TOKEN]

    def tearDown(self):
        pass

    def test_proxy_failure(self):
        client: WebClient = WebClient(
            token=self.bot_token,
            run_async=False,
            proxy=self.proxy,
            loop=asyncio.new_event_loop())
        with self.assertRaises(URLError):
            client.auth_test()

    @async_test
    async def test_proxy_failure_async(self):
        client: WebClient = WebClient(
            token=self.bot_token,
            proxy=self.proxy,
            run_async=True
        )
        with self.assertRaises(ClientConnectorError):
            await client.auth_test()
