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

    https://github.com/slackapi/python-slackclient/issues/558
    """

    def setUp(self):
        self.logger = logging.getLogger(__name__)
        self.bot_token = os.environ[SLACK_SDK_TEST_CLASSIC_APP_BOT_TOKEN]

    def tearDown(self):
        # Reset the decorators by @RTMClient.run_on
        RTMClient._callbacks = collections.defaultdict(list)

    @pytest.mark.skipif(condition=is_not_specified(), reason="Still unfixed")
    @async_test
    async def test_issue_558(self):
        channel_id = os.environ[SLACK_SDK_TEST_RTM_TEST_CHANNEL_ID]
        text = "This message was sent by <https://slack.dev/python-slackclient/|python-slackclient>! (test_issue_558)"

        self.message_count, self.reaction_count = 0, 0

        async def process_messages(**payload):
            self.logger.debug(payload)
            self.message_count += 1
            await asyncio.sleep(10)  # this used to block all other handlers

        async def process_reactions(**payload):
            self.logger.debug(payload)
            self.reaction_count += 1

        rtm = RTMClient(token=self.bot_token, run_async=True)
        RTMClient.on(event='message', callback=process_messages)
        RTMClient.on(event='reaction_added', callback=process_reactions)

        web_client = WebClient(token=self.bot_token, run_async=True)
        message = await web_client.chat_postMessage(channel=channel_id, text=text)
        self.assertFalse("error" in message)
        ts = message["ts"]
        await asyncio.sleep(3)

        # intentionally not waiting here
        rtm.start()
        await asyncio.sleep(3)

        try:
            first_reaction = await web_client.reactions_add(channel=channel_id, timestamp=ts, name="eyes")
            self.assertFalse("error" in first_reaction)
            await asyncio.sleep(2)

            message = await web_client.chat_postMessage(channel=channel_id, text=text)
            self.assertFalse("error" in message)
            # used to start blocking here

            # This reaction_add event won't be handled due to a bug
            second_reaction = await web_client.reactions_add(channel=channel_id, timestamp=ts, name="tada")
            self.assertFalse("error" in second_reaction)
            await asyncio.sleep(2)

            self.assertEqual(self.message_count, 1)
            self.assertEqual(self.reaction_count, 2)  # used to fail
        finally:
            if not rtm._stopped:
                rtm.stop()
