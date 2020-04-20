import asyncio
import collections
import logging
import os
import threading
import time
import traceback
import unittest

import psutil
import pytest

from integration_tests.env_variable_names import SLACK_SDK_TEST_CLASSIC_APP_BOT_TOKEN, \
    SLACK_SDK_TEST_RTM_TEST_CHANNEL_ID
from integration_tests.helpers import async_test
from slack import RTMClient, WebClient


class TestRTMClient(unittest.TestCase):
    """Runs integration tests with real Slack API"""

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

    def tearDown(self):
        # Reset the decorators by @RTMClient.run_on
        RTMClient._callbacks = collections.defaultdict(list)
        # Stop the Client
        if not self.rtm_client._stopped:
            self.rtm_client.stop()

    def test_basic_operations(self):
        self.sent_text: str = None
        self.rtm_client = RTMClient(
            token=self.bot_token,
            run_async=False,
            loop=asyncio.new_event_loop(),  # TODO: this doesn't work without this
        )
        self.web_client = WebClient(
            token=self.bot_token,
            run_async=False,
            loop=asyncio.new_event_loop(),  # TODO: this doesn't work without this
        )

        @RTMClient.run_on(event="message")
        def send_reply(**payload):
            self.logger.debug(payload)
            self.sent_text = payload['data']['text']

        def connect():
            self.logger.debug("Starting RTM Client...")
            self.rtm_client.start()

        t = threading.Thread(target=connect)
        t.setDaemon(True)
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
            t.join(.3)

    @async_test
    async def test_basic_operations_async(self):
        self.sent_text: str = None
        self.rtm_client = RTMClient(token=self.bot_token, run_async=True)
        self.async_web_client = WebClient(token=self.bot_token, run_async=True)

        @RTMClient.run_on(event="message")
        async def send_reply(**payload):
            self.logger.debug(payload)
            self.sent_text = payload['data']['text']

        # intentionally not waiting here
        self.rtm_client.start()

        self.assertIsNone(self.sent_text)
        await asyncio.sleep(5)

        text = "This message was sent by <https://slack.dev/python-slackclient/|python-slackclient>! (test_basic_operations_async)"
        new_message = await self.async_web_client.chat_postMessage(
            channel="CHE2DUW5V",
            text=text
        )
        self.assertFalse("error" in new_message)
        await asyncio.sleep(5)
        self.assertEqual(self.sent_text, text)

    # TODO: Fix this issue
    @pytest.mark.skip("This needs to be fixed - https://github.com/slackapi/python-slackclient/issues/569")
    def test_cpu_usage(self):
        self.rtm_client = RTMClient(
            token=self.bot_token,
            run_async=False,
            loop=asyncio.new_event_loop())
        self.web_client = WebClient(
            token=self.bot_token,
            run_async=False,
            loop=asyncio.new_event_loop())

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

    # -----------------------
    # Issue #631
    # https://github.com/slackapi/python-slackclient/issues/631
    # -----------------------

    @pytest.mark.skip() # TODO: this issue needs to be fixed
    def test_issue_631_sharing_event_loop(self):
        self.success = None
        self.text = "This message was sent to verify issue #631"

        self.loop = asyncio.get_event_loop()
        self.rtm_client = RTMClient(
            token=self.bot_token,
            run_async=False, # even though run_async=False, handlers for RTM events can be a coroutine
            loop=self.loop,
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
        # even though run_async=False, handlers for RTM events can be a coroutine
        async def send_reply(**payload):
            self.logger.debug(payload)
            data = payload['data']
            web_client = payload['web_client']
            web_client._event_loop = self.loop

            try:
                if "text" in data and self.text in data["text"]:
                    channel_id = data['channel']
                    thread_ts = data['ts']
                    self.success = await web_client.chat_postMessage(
                        channel=channel_id,
                        text="Thanks!",
                        thread_ts=thread_ts
                    )
            except Exception as e:
                self.logger.error(traceback.format_exc())
                raise e

        def connect():
            self.logger.debug("Starting RTM Client...")
            self.rtm_client.start()

        t = threading.Thread(target=connect)
        t.setDaemon(True)
        t.start()

        try:
            self.assertIsNone(self.success)
            time.sleep(5)

            self.web_client = WebClient(
                token=self.bot_token,
                run_async=False,
                loop=asyncio.new_event_loop(),  # TODO: this doesn't work without this
            )
            new_message = self.web_client.chat_postMessage(channel=self.channel_id, text=self.text)
            self.assertFalse("error" in new_message)

            time.sleep(5)
            self.assertIsNotNone(self.success)
        finally:
            t.join(.3)

    # Solution (2) for #631
    @pytest.mark.skip("this is just for your reference")
    @async_test
    async def test_issue_631_sharing_event_loop_async(self):
        self.loop = asyncio.get_event_loop()
        self.success = None
        self.text = "This message was sent to verify issue #631"

        self.rtm_client = RTMClient(
            token=self.bot_token,
            run_async=True, # To turn this on, the test method needs to be an async function + @async_test decorator
        )

        @RTMClient.run_on(event="message")
        async def send_reply(**payload):
            self.logger.debug(payload)
            data = payload['data']
            web_client = payload['web_client']
            web_client._event_loop = self.loop

            try:
                if "text" in data and self.text in data["text"]:
                    channel_id = data['channel']
                    thread_ts = data['ts']
                    self.success = await web_client.chat_postMessage(
                        channel=channel_id,
                        text="Thanks!",
                        thread_ts=thread_ts
                    )
            except Exception as e:
                self.logger.error(traceback.format_exc())
                raise e

        # intentionally not waiting here
        self.rtm_client.start()

        self.assertIsNone(self.success)
        await asyncio.sleep(5)

        self.web_client = WebClient(
            token=self.bot_token,
            run_async=True, # all need to be async here
        )
        new_message = await self.web_client.chat_postMessage(channel=self.channel_id, text=self.text)
        self.assertFalse("error" in new_message)

        await asyncio.sleep(5)
        self.assertIsNotNone(self.success)
