import asyncio
import collections
import logging
import os
import threading
import time
import unittest

import psutil
import pytest

from integration_tests.env_variable_names import \
    SLACK_SDK_TEST_CLASSIC_APP_BOT_TOKEN, \
    SLACK_SDK_TEST_RTM_TEST_CHANNEL_ID
from integration_tests.helpers import async_test, is_not_specified
from slack import RTMClient, WebClient


class TestRTMClient(unittest.TestCase):
    """Runs integration tests with real Slack API

    https://github.com/slackapi/python-slackclient/issues/569
    """

    def setUp(self):
        if not hasattr(self, "logger"):
            self.logger = logging.getLogger(__name__)
            self.channel_id = os.environ[SLACK_SDK_TEST_RTM_TEST_CHANNEL_ID]
            self.bot_token = os.environ[SLACK_SDK_TEST_CLASSIC_APP_BOT_TOKEN]

        if not hasattr(self, "cpu_monitor") or not TestRTMClient.cpu_monitor.is_alive():
            def run_cpu_monitor(self):
                self.logger.debug("Starting CPU monitor in another thread...")
                TestRTMClient.cpu_usage = 0
                while True:
                    p = psutil.Process(os.getpid())
                    current_cpu_usage: float = p.cpu_percent(interval=0.5)
                    self.logger.debug(current_cpu_usage)
                    if current_cpu_usage > TestRTMClient.cpu_usage:
                        TestRTMClient.cpu_usage = current_cpu_usage

            TestRTMClient.cpu_monitor = threading.Thread(target=run_cpu_monitor, args=[self])
            TestRTMClient.cpu_monitor.setDaemon(True)
            TestRTMClient.cpu_monitor.start()

        self.rtm_client = None
        self.web_client = None

    def tearDown(self):
        # Reset the decorators by @RTMClient.run_on
        RTMClient._callbacks = collections.defaultdict(list)
        # Stop the Client
        if hasattr(self, "rtm_client") and not self.rtm_client._stopped:
            self.rtm_client.stop()

    @pytest.mark.skipif(condition=is_not_specified(), reason="To avoid rate_limited errors")
    def test_cpu_usage(self):
        self.rtm_client = RTMClient(token=self.bot_token, run_async=False, loop=asyncio.new_event_loop())
        self.web_client = WebClient(token=self.bot_token, run_async=False)

        self.call_count = 0
        TestRTMClient.cpu_usage = 0

        @RTMClient.run_on(event="message")
        def send_reply(**payload):
            self.logger.debug(payload)
            event = payload["data"]
            if "text" in event:
                if not str(event["text"]).startswith("Current CPU usage:"):
                    web_client = payload["web_client"]
                    for i in range(0, 3):
                        new_message = web_client.chat_postMessage(
                            channel=event["channel"],
                            text=f"Current CPU usage: {TestRTMClient.cpu_usage} % (test_cpu_usage)"
                        )
                        self.logger.debug(new_message)
                        self.call_count += 1

        def connect():
            self.logger.debug("Starting RTM Client...")
            self.rtm_client.start()

        rtm = threading.Thread(target=connect)
        rtm.setDaemon(True)

        rtm.start()
        time.sleep(5)

        text = "This message was sent by <https://slack.dev/python-slackclient/|python-slackclient>! (test_cpu_usage)"
        new_message = self.web_client.chat_postMessage(channel=self.channel_id, text=text)
        self.assertFalse("error" in new_message)

        time.sleep(5)
        self.assertLess(TestRTMClient.cpu_usage, 30, "Too high CPU usage detected")
        self.assertEqual(self.call_count, 3, "The RTM handler failed")

    # >       self.assertLess(TestRTMClient.cpu_usage, 30, "Too high CPU usage detected")
    # E       AssertionError: 100.2 not less than 30 : Too high CPU usage detected
    #
    # integration_tests/rtm/test_rtm_client.py:160: AssertionError

    @async_test
    async def test_cpu_usage_async(self):
        self.rtm_client = RTMClient(token=self.bot_token, run_async=True)
        self.web_client = WebClient(token=self.bot_token, run_async=True)

        self.call_count = 0
        TestRTMClient.cpu_usage = 0

        @RTMClient.run_on(event="message")
        async def send_reply_async(**payload):
            self.logger.debug(payload)
            event = payload["data"]
            if "text" in event:
                if not str(event["text"]).startswith("Current CPU usage:"):
                    web_client = payload["web_client"]
                    for i in range(0, 3):
                        new_message = await web_client.chat_postMessage(
                            channel=event["channel"],
                            text=f"Current CPU usage: {TestRTMClient.cpu_usage} % (test_cpu_usage_async)"
                        )
                        self.logger.debug(new_message)
                        self.call_count += 1

        # intentionally not waiting here
        self.rtm_client.start()

        await asyncio.sleep(5)

        text = "This message was sent by <https://slack.dev/python-slackclient/|python-slackclient>! (test_cpu_usage_async)"
        new_message = await self.web_client.chat_postMessage(channel=self.channel_id, text=text)
        self.assertFalse("error" in new_message)

        await asyncio.sleep(5)
        self.assertLess(TestRTMClient.cpu_usage, 30, "Too high CPU usage detected")
        self.assertEqual(self.call_count, 3, "The RTM handler failed")
