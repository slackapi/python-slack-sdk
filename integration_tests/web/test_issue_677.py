import asyncio
import logging
import os
import unittest
from datetime import datetime

from integration_tests.env_variable_names import \
    SLACK_SDK_TEST_BOT_TOKEN, \
    SLACK_SDK_TEST_WEB_TEST_CHANNEL_ID
from integration_tests.helpers import async_test
from slack import WebClient
from slack.web.classes.objects import DateLink


class TestWebClient(unittest.TestCase):
    """Runs integration tests with real Slack API

    https://github.com/slackapi/python-slackclient/issues/677
    """

    def setUp(self):
        if not hasattr(self, "logger"):
            self.logger = logging.getLogger(__name__)
            self.bot_token = os.environ[SLACK_SDK_TEST_BOT_TOKEN]
            self.sync_client: WebClient = WebClient(
                token=self.bot_token,
                run_async=False,
                loop=asyncio.new_event_loop())
            self.async_client: WebClient = WebClient(token=self.bot_token, run_async=True)
            self.channel_id = os.environ[SLACK_SDK_TEST_WEB_TEST_CHANNEL_ID]

    def tearDown(self):
        pass

    def test_date_link(self):
        client = self.sync_client
        link = DateLink(
            date=datetime.now(),
            date_format="{date_long} {time}",
            fallback="fallback string",
            link="https://www.example.com"
        )
        message = f"Here is a date link: {link}"
        response = client.chat_postMessage(channel=self.channel_id, text=message)
        self.assertIsNotNone(response)
        self.assertRegex(
            r"Here is a date link: <!date^\d+^{date_long} {time}^https://www.example.com|fallback string>",
            response["message"]["text"],
        )

    @async_test
    async def test_date_link_async(self):
        client = self.async_client
        link = DateLink(
            date=datetime.now(),
            date_format="{date_long} {time}",
            fallback="fallback string",
            link="https://www.example.com"
        )
        message = f"Here is a date link: {link}"
        response = await client.chat_postMessage(channel=self.channel_id, text=message)
        self.assertIsNotNone(response)
        self.assertRegex(
            r"Here is a date link: <!date^\d+^{date_long} {time}^https://www.example.com|fallback string>",
            response["message"]["text"],
        )
