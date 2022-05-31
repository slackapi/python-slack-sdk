import asyncio
import collections
import logging
import os
import threading
import time
import traceback
import unittest

import pytest

from integration_tests.env_variable_names import (
    SLACK_SDK_TEST_CLASSIC_APP_BOT_TOKEN,
    SLACK_SDK_TEST_RTM_TEST_CHANNEL_ID,
)
from integration_tests.helpers import async_test, is_not_specified
from slack_sdk.rtm import RTMClient
from slack_sdk.web import WebClient


class TestRTMClient(unittest.TestCase):
    """Runs integration tests with real Slack API

    https://github.com/slackapi/python-slack-sdk/issues/631
    """

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

    @pytest.mark.skipif(condition=is_not_specified(), reason="to avoid rate_limited errors")
    def test_issue_631_sharing_event_loop(self):
        self.success = None
        self.text = "This message was sent to verify issue #631"

        self.rtm_client = RTMClient(
            token=self.bot_token,
            run_async=False,
            loop=asyncio.new_event_loop(),  # TODO: this doesn't work without this
        )

        # @RTMClient.run_on(event="message")
        # def send_reply(**payload):
        #     self.logger.debug(payload)
        #     data = payload['data']
        #     web_client = payload['web_client']
        #     web_client._event_loop = self.loop
        #     # Maybe you will also need the following line uncommented
        #     # web_client.run_async = True
        #
        #     if self.text in data['text']:
        #         channel_id = data['channel']
        #         thread_ts = data['ts']
        #         try:
        #             self.success = web_client.chat_postMessage(
        #                 channel=channel_id,
        #                 text="Thanks!",
        #                 thread_ts=thread_ts
        #             )
        #         except Exception as e:
        #             # slack.rtm.client:client.py:446 When calling '#send_reply()'
        #             # in the 'test_rtm_client' module the following error was raised: This event loop is already running
        #             self.logger.error(traceback.format_exc())
        #             raise e

        # Solution (1) for #631
        @RTMClient.run_on(event="message")
        def send_reply(**payload):
            self.logger.debug(payload)
            data = payload["data"]
            web_client = payload["web_client"]

            try:
                if "text" in data and self.text in data["text"]:
                    channel_id = data["channel"]
                    thread_ts = data["ts"]
                    self.success = web_client.chat_postMessage(channel=channel_id, text="Thanks!", thread_ts=thread_ts)
            except Exception as e:
                self.logger.error(traceback.format_exc())
                raise e

        def connect():
            self.logger.debug("Starting RTM Client...")
            self.rtm_client.start()

        t = threading.Thread(target=connect)
        t.daemon = True
        t.start()

        try:
            self.assertIsNone(self.success)
            time.sleep(5)

            self.web_client = WebClient(
                token=self.bot_token,
                run_async=False,
            )
            new_message = self.web_client.chat_postMessage(channel=self.channel_id, text=self.text)
            self.assertFalse("error" in new_message)

            time.sleep(5)
            self.assertIsNotNone(self.success)
        finally:
            t.join(0.3)

    # Solution (2) for #631
    @pytest.mark.skipif(condition=is_not_specified(), reason="this is just for reference")
    @async_test
    async def test_issue_631_sharing_event_loop_async(self):
        self.success = None
        self.text = "This message was sent to verify issue #631"

        # To make run_async=True, the test method needs to be an async function + @async_test decorator
        self.rtm_client = RTMClient(token=self.bot_token, run_async=True)
        self.web_client = WebClient(token=self.bot_token, run_async=True)

        @RTMClient.run_on(event="message")
        async def send_reply(**payload):
            self.logger.debug(payload)
            data = payload["data"]
            web_client = payload["web_client"]

            try:
                if "text" in data and self.text in data["text"]:
                    channel_id = data["channel"]
                    thread_ts = data["ts"]
                    self.success = await web_client.chat_postMessage(channel=channel_id, text="Thanks!", thread_ts=thread_ts)
            except Exception as e:
                self.logger.error(traceback.format_exc())
                raise e

        # intentionally not waiting here
        self.rtm_client.start()

        self.assertIsNone(self.success)
        await asyncio.sleep(5)

        self.web_client = WebClient(
            token=self.bot_token,
            run_async=True,  # all need to be async here
        )
        new_message = await self.web_client.chat_postMessage(channel=self.channel_id, text=self.text)
        self.assertFalse("error" in new_message)

        await asyncio.sleep(5)
        self.assertIsNotNone(self.success)
