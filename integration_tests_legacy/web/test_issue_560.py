import logging
import os
import unittest

from integration_tests.env_variable_names import SLACK_SDK_TEST_BOT_TOKEN
from integration_tests.helpers import async_test
from slack import WebClient


class TestWebClient(unittest.TestCase):
    """Runs integration tests with real Slack API

    https://github.com/slackapi/python-slackclient/issues/560
    """

    def setUp(self):
        self.logger = logging.getLogger(__name__)
        self.bot_token = os.environ[SLACK_SDK_TEST_BOT_TOKEN]
        self.sync_client: WebClient = WebClient(token=self.bot_token, run_async=False)
        self.async_client: WebClient = WebClient(token=self.bot_token, run_async=True)

    def tearDown(self):
        pass

    def test_issue_560_success(self):
        client = self.sync_client
        response = client.conversations_list(exclude_archived=1)
        self.assertIsNotNone(response)

        response = client.conversations_list(exclude_archived="true")
        self.assertIsNotNone(response)

    @async_test
    async def test_issue_560_success_async(self):
        client = self.async_client
        response = await client.conversations_list(exclude_archived=1)
        self.assertIsNotNone(response)

        response = await client.conversations_list(exclude_archived="true")
        self.assertIsNotNone(response)

    def test_issue_560_failure(self):
        client = self.sync_client
        response = client.conversations_list(exclude_archived=True)
        self.assertIsNotNone(response)

    @async_test
    async def test_issue_560_failure_async(self):
        client = self.async_client
        response = await client.conversations_list(exclude_archived=True)
        self.assertIsNotNone(response)
