import asyncio
import collections
import logging
import os
import threading
import time
import unittest

from integration_tests.env_variable_names import (
    SLACK_SDK_TEST_CLASSIC_APP_BOT_TOKEN,
    SLACK_SDK_TEST_RTM_TEST_CHANNEL_ID,
)
from integration_tests.helpers import async_test
from slack_sdk.rtm import RTMClient
from slack_sdk.web.legacy_client import LegacyWebClient


class TestRTMClient(unittest.TestCase):
    """Runs integration tests with real Slack API"""

    def setUp(self):
        if not hasattr(self, "logger"):
            self.logger = logging.getLogger(__name__)
            self.channel_id = os.environ[SLACK_SDK_TEST_RTM_TEST_CHANNEL_ID]
            self.bot_token = os.environ[SLACK_SDK_TEST_CLASSIC_APP_BOT_TOKEN]

    def tearDown(self):
        # Reset the decorators by @RTMClient.run_on
        RTMClient._callbacks = collections.defaultdict(list)
        # Stop the Client
        if hasattr(self, "rtm_client") and not self.rtm_client._stopped:
            self.rtm_client.stop()

    def test_basic_operations(self):
        self.sent_text: str = None
        self.rtm_client = RTMClient(
            token=self.bot_token,
            run_async=False,
            loop=asyncio.new_event_loop(),  # TODO: this doesn't work without this
        )
        self.web_client = LegacyWebClient(token=self.bot_token)

        @RTMClient.run_on(event="message")
        def send_reply(**payload):
            self.logger.debug(payload)
            self.sent_text = payload["data"]["text"]

        def connect():
            self.logger.debug("Starting RTM Client...")
            self.rtm_client.start()

        t = threading.Thread(target=connect)
        t.daemon = True
        t.start()

        try:
            self.assertIsNone(self.sent_text)
            time.sleep(5)

            text = "This message was sent by <https://slack.dev/python-slackclient/|python-slackclient>! (test_basic_operations)"
            new_message = self.web_client.chat_postMessage(channel=self.channel_id, text=text)
            self.assertFalse("error" in new_message)

            time.sleep(5)
            self.assertEqual(self.sent_text, text)
        finally:
            t.join(0.3)

    @async_test
    async def test_basic_operations_async(self):
        self.sent_text: str = None
        self.rtm_client = RTMClient(token=self.bot_token, run_async=True)
        self.async_web_client = LegacyWebClient(token=self.bot_token, run_async=True)

        @RTMClient.run_on(event="message")
        async def send_reply(**payload):
            self.logger.debug(payload)
            self.sent_text = payload["data"]["text"]

        # intentionally not waiting here
        self.rtm_client.start()

        self.assertIsNone(self.sent_text)
        await asyncio.sleep(5)

        text = "This message was sent by <https://slack.dev/python-slackclient/|python-slackclient>! (test_basic_operations_async)"
        new_message = await self.async_web_client.chat_postMessage(channel=self.channel_id, text=text)
        self.assertFalse("error" in new_message)
        await asyncio.sleep(5)
        self.assertEqual(self.sent_text, text)
