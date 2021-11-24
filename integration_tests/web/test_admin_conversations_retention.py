import asyncio
import logging
import os
import time
import unittest

from integration_tests.env_variable_names import (
    SLACK_SDK_TEST_GRID_ORG_ADMIN_USER_TOKEN,
    SLACK_SDK_TEST_GRID_TEAM_ID,
)
from integration_tests.helpers import async_test
from slack_sdk.web import WebClient
from slack_sdk.web.async_client import AsyncWebClient


class TestWebClient(unittest.TestCase):
    """Runs integration tests with real Slack API"""

    def setUp(self):
        self.logger = logging.getLogger(__name__)
        self.org_admin_token = os.environ[SLACK_SDK_TEST_GRID_ORG_ADMIN_USER_TOKEN]
        self.team_id = os.environ[SLACK_SDK_TEST_GRID_TEAM_ID]
        self.sync_client: WebClient = WebClient(token=self.org_admin_token)
        self.async_client: AsyncWebClient = AsyncWebClient(token=self.org_admin_token)

        self.channel_name = f"test-channel-{int(round(time.time() * 1000))}"

    def tearDown(self):
        pass

    def test_sync(self):
        client = self.sync_client

        conv_creation = client.admin_conversations_create(
            is_private=False,
            name=self.channel_name,
            team_id=self.team_id,
        )
        self.assertIsNotNone(conv_creation)
        created_channel_id = conv_creation.data["channel_id"]

        self.assertIsNotNone(
            client.admin_conversations_setCustomRetention(
                channel_id=created_channel_id,
                duration_days=365,
            )
        )
        self.assertIsNotNone(
            client.admin_conversations_getCustomRetention(
                channel_id=created_channel_id,
            )
        )
        self.assertIsNotNone(
            client.admin_conversations_removeCustomRetention(
                channel_id=created_channel_id,
            )
        )

        time.sleep(2)  # To avoid internal_error
        self.assertIsNotNone(
            client.admin_conversations_delete(
                channel_id=created_channel_id,
            )
        )

    @async_test
    async def test_async(self):
        # await asyncio.sleep(seconds) are included to avoid rate limiting errors

        client = self.async_client

        conv_creation = await client.admin_conversations_create(
            is_private=False,
            name=self.channel_name,
            team_id=self.team_id,
        )
        self.assertIsNotNone(conv_creation)
        created_channel_id = conv_creation.data["channel_id"]

        self.assertIsNotNone(
            await client.admin_conversations_setCustomRetention(
                channel_id=created_channel_id,
                duration_days=365,
            )
        )
        self.assertIsNotNone(
            await client.admin_conversations_getCustomRetention(
                channel_id=created_channel_id,
            )
        )
        self.assertIsNotNone(
            await client.admin_conversations_removeCustomRetention(
                channel_id=created_channel_id,
            )
        )

        await asyncio.sleep(2)  # To avoid internal_error
        self.assertIsNotNone(
            await client.admin_conversations_delete(
                channel_id=created_channel_id,
            )
        )
