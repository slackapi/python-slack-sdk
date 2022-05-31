import asyncio
import collections
import logging
import os
import threading
import time
import unittest

import pytest

from integration_tests.env_variable_names import SLACK_SDK_TEST_CLASSIC_APP_BOT_TOKEN
from integration_tests.helpers import async_test, is_not_specified
from slack_sdk.rtm import RTMClient
from slack_sdk.web import WebClient


class TestRTMClient(unittest.TestCase):
    """Runs integration tests with real Slack API

    https://github.com/slackapi/python-slack-sdk/issues/701
    """

    def setUp(self):
        self.logger = logging.getLogger(__name__)
        self.bot_token = os.environ[SLACK_SDK_TEST_CLASSIC_APP_BOT_TOKEN]

    def tearDown(self):
        # Reset the decorators by @RTMClient.run_on
        RTMClient._callbacks = collections.defaultdict(list)

    # @pytest.mark.skipif(condition=is_not_specified(), reason="to avoid rate_limited errors")
    @pytest.mark.skip()
    def test_receiving_all_messages(self):
        self.rtm_client = RTMClient(token=self.bot_token, loop=asyncio.new_event_loop())
        self.web_client = WebClient(token=self.bot_token)

        self.call_count = 0

        @RTMClient.run_on(event="message")
        def send_reply(**payload):
            self.logger.debug(payload)
            web_client, data = payload["web_client"], payload["data"]
            web_client.reactions_add(channel=data["channel"], timestamp=data["ts"], name="eyes")
            self.call_count += 1

        def connect():
            self.logger.debug("Starting RTM Client...")
            self.rtm_client.start()

        rtm = threading.Thread(target=connect)
        rtm.daemon = True

        rtm.start()
        time.sleep(3)

        total_num = 10

        sender_completion = []

        def sent_bulk_message():
            for i in range(total_num):
                text = f"Sent by <https://slack.dev/python-slackclient/|python-slackclient>! ({i})"
                self.web_client.chat_postMessage(channel="#random", text=text)
                time.sleep(0.1)
            sender_completion.append(True)

        num_of_senders = 3
        senders = []
        for sender_num in range(num_of_senders):
            sender = threading.Thread(target=sent_bulk_message)
            sender.daemon = True
            sender.start()
            senders.append(sender)

        while len(sender_completion) < num_of_senders:
            time.sleep(1)

        expected_call_count = total_num * num_of_senders
        wait_seconds = 0
        max_wait = 20
        while self.call_count < expected_call_count and wait_seconds < max_wait:
            time.sleep(1)
            wait_seconds += 1

        self.assertEqual(total_num * num_of_senders, self.call_count, "The RTM handler failed")

    @pytest.mark.skipif(condition=is_not_specified(), reason="to avoid rate_limited errors")
    @async_test
    async def test_receiving_all_messages_async(self):
        self.rtm_client = RTMClient(token=self.bot_token, run_async=True)
        self.web_client = WebClient(token=self.bot_token, run_async=False)

        self.call_count = 0

        @RTMClient.run_on(event="message")
        async def send_reply(**payload):
            self.logger.debug(payload)
            web_client, data = payload["web_client"], payload["data"]
            await web_client.reactions_add(channel=data["channel"], timestamp=data["ts"], name="eyes")
            self.call_count += 1

        # intentionally not waiting here
        self.rtm_client.start()

        await asyncio.sleep(3)

        total_num = 10

        sender_completion = []

        def sent_bulk_message():
            for i in range(total_num):
                text = f"Sent by <https://slack.dev/python-slackclient/|python-slackclient>! ({i})"
                self.web_client.chat_postMessage(channel="#random", text=text)
                time.sleep(0.1)
            sender_completion.append(True)

        num_of_senders = 3
        senders = []
        for sender_num in range(num_of_senders):
            sender = threading.Thread(target=sent_bulk_message)
            sender.daemon = True
            sender.start()
            senders.append(sender)

        while len(sender_completion) < num_of_senders:
            await asyncio.sleep(1)

        expected_call_count = total_num * num_of_senders
        wait_seconds = 0
        max_wait = 20
        while self.call_count < expected_call_count and wait_seconds < max_wait:
            await asyncio.sleep(1)
            wait_seconds += 1

        self.assertEqual(total_num * num_of_senders, self.call_count, "The RTM handler failed")
