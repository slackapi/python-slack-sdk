import asyncio
import logging
import os
import unittest

from integration_tests.env_variable_names import SLACK_SDK_TEST_USER_TOKEN
from integration_tests.helpers import async_test
from slack import WebClient


class TestWebClient(unittest.TestCase):
    """Runs integration tests with real Slack API

    https://github.com/slackapi/python-slackclient/issues/378
    """

    def setUp(self):
        self.logger = logging.getLogger(__name__)
        self.user_token = os.environ[SLACK_SDK_TEST_USER_TOKEN]
        self.sync_client: WebClient = WebClient(token=self.user_token, run_async=False, loop=asyncio.new_event_loop())
        self.async_client: WebClient = WebClient(token=self.user_token, run_async=True)

    def tearDown(self):
        pass

    def test_issue_378(self):
        client = self.sync_client
        response = client.users_setPhoto(image="tests/data/slack_logo_new.png")
        self.assertIsNotNone(response)

    @async_test
    async def test_issue_378_async(self):
        client = self.async_client
        response = await client.users_setPhoto(image="tests/data/slack_logo_new.png")
        self.assertIsNotNone(response)
