import asyncio
import collections
import logging
import os
import unittest

import pytest

from integration_tests.env_variable_names import \
    SLACK_SDK_TEST_CLASSIC_APP_BOT_TOKEN, \
    SLACK_SDK_TEST_RTM_TEST_CHANNEL_ID
from integration_tests.helpers import async_test, is_not_specified
from slack import RTMClient, WebClient


class TestRTMClient(unittest.TestCase):
    """Runs integration tests with real Slack API

    https://github.com/slackapi/python-slackclient/issues/611
    """

    def setUp(self):
        self.logger = logging.getLogger(__name__)
        self.bot_token = os.environ[SLACK_SDK_TEST_CLASSIC_APP_BOT_TOKEN]

    def tearDown(self):
        # Reset the decorators by @RTMClient.run_on
        RTMClient._callbacks = collections.defaultdict(list)

    @pytest.mark.skipif(condition=is_not_specified(), reason="To avoid rate limited errors")
    @async_test
    async def test_issue_611(self):
        channel_id = os.environ[SLACK_SDK_TEST_RTM_TEST_CHANNEL_ID]
        text = "This message was sent by <https://slack.dev/python-slackclient/|python-slackclient>! (test_issue_611)"

        self.message_count, self.reaction_count = 0, 0

        async def process_messages(**payload):
            self.logger.info(payload)
            if "subtype" in payload["data"] and payload["data"]["subtype"] == "message_replied":
                return  # skip

            self.message_count += 1
            raise Exception("something is wrong!")  # This causes the termination of the process

        async def process_reactions(**payload):
            self.logger.info(payload)
            self.reaction_count += 1

        rtm = RTMClient(token=self.bot_token, run_async=True)
        RTMClient.on(event='message', callback=process_messages)
        RTMClient.on(event='reaction_added', callback=process_reactions)

        web_client = WebClient(token=self.bot_token, run_async=True)
        message = await web_client.chat_postMessage(channel=channel_id, text=text)
        ts = message["ts"]

        await asyncio.sleep(3)

        # intentionally not waiting here
        rtm.start()

        try:
            await asyncio.sleep(3)

            first_reaction = await web_client.reactions_add(channel=channel_id, timestamp=ts, name="eyes")
            self.assertFalse("error" in first_reaction)
            await asyncio.sleep(2)

            should_be_ignored = await web_client.chat_postMessage(channel=channel_id, text="Hello?", thread_ts=ts)
            self.assertFalse("error" in should_be_ignored)
            await asyncio.sleep(2)

            second_reaction = await web_client.reactions_add(channel=channel_id, timestamp=ts, name="tada")
            self.assertFalse("error" in second_reaction)
            await asyncio.sleep(2)

            self.assertEqual(self.message_count, 1)
            self.assertEqual(self.reaction_count, 2)
        finally:
            if not rtm._stopped:
                rtm.stop()
