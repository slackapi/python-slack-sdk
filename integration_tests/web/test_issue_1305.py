import asyncio
import os
import time
import unittest

from integration_tests.env_variable_names import SLACK_SDK_TEST_GRID_ORG_ADMIN_USER_TOKEN
from integration_tests.helpers import async_test
from slack_sdk.web import WebClient
from slack_sdk.web.async_client import AsyncWebClient


class TestWebClient(unittest.TestCase):
    """Runs integration tests with real Slack API

    https://github.com/slackapi/python-slack-sdk/issues/1305
    """

    def setUp(self):
        self.org_admin_token = os.environ[SLACK_SDK_TEST_GRID_ORG_ADMIN_USER_TOKEN]
        self.sync_client: WebClient = WebClient(token=self.org_admin_token)
        self.async_client: AsyncWebClient = AsyncWebClient(token=self.org_admin_token)

    def tearDown(self):
        pass

    def test_sync(self):
        client = self.sync_client
        count = 0

        for page in client.admin_conversations_search(limit=1):
            count += len(page["conversations"])
            if count > 1:
                break
            time.sleep(1)

        self.assertGreater(count, 0)

    @async_test
    async def test_async(self):
        client = self.async_client
        count = 0

        async for page in await client.admin_conversations_search(limit=1):
            count += len(page["conversations"])
            if count > 1:
                break
            await asyncio.sleep(1)

        self.assertGreater(count, 0)
