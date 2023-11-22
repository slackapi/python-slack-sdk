import asyncio
import logging
import os
import time
import unittest

from integration_tests.env_variable_names import (
    SLACK_SDK_TEST_GRID_WORKSPACE_ADMIN_USER_TOKEN,
    SLACK_SDK_TEST_GRID_ORG_ADMIN_USER_TOKEN,
    SLACK_SDK_TEST_GRID_IDP_USERGROUP_ID,
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
        self.sync_client: WebClient = WebClient(token=self.org_admin_token)
        self.async_client: AsyncWebClient = AsyncWebClient(token=self.org_admin_token)

        self.team_id = os.environ[SLACK_SDK_TEST_GRID_TEAM_ID]
        self.idp_group_id = os.environ[SLACK_SDK_TEST_GRID_IDP_USERGROUP_ID]

        if not hasattr(self, "channel_id"):
            team_admin_token = os.environ[SLACK_SDK_TEST_GRID_WORKSPACE_ADMIN_USER_TOKEN]
            client = WebClient(token=team_admin_token)
            # Only fetching private channels since admin.conversations.restrictAccess methods
            # do not work for public channels
            convs = client.conversations_list(exclude_archived=True, limit=100, types="private_channel")
            self.channel_id = next(
                (c["id"] for c in convs["channels"] if c["name"] != "general" and not c["is_ext_shared"]),
                None,
            )
            if self.channel_id is None:
                millis = int(round(time.time() * 1000))
                channel_name = f"private-test-channel-{millis}"
                self.channel_id = client.conversations_create(name=channel_name, is_private=True,)[
                    "channel"
                ]["id"]

    def tearDown(self):
        pass

    def test_sync(self):
        # time.sleep(seconds) are included to avoid rate limiting errors
        client = self.sync_client

        add_group = client.admin_conversations_restrictAccess_addGroup(
            channel_id=self.channel_id, group_id=self.idp_group_id, team_id=self.team_id
        )
        self.assertIsNotNone(add_group)
        # To avoid rate limiting errors
        time.sleep(10)

        list_groups = client.admin_conversations_restrictAccess_listGroups(team_id=self.team_id, channel_id=self.channel_id)
        self.assertIsNotNone(list_groups)
        # To avoid rate limiting errors
        time.sleep(10)

        remove_group = client.admin_conversations_restrictAccess_removeGroup(
            channel_id=self.channel_id, group_id=self.idp_group_id, team_id=self.team_id
        )
        self.assertIsNotNone(remove_group)
        # To avoid rate limiting errors
        time.sleep(20)

    @async_test
    async def test_async(self):
        # await asyncio.sleep(seconds) are included to avoid rate limiting errors

        client = self.async_client

        add_group = await client.admin_conversations_restrictAccess_addGroup(
            channel_id=self.channel_id, group_id=self.idp_group_id, team_id=self.team_id
        )
        self.assertIsNotNone(add_group)
        # To avoid rate limiting errors
        await asyncio.sleep(10)

        list_groups = await client.admin_conversations_restrictAccess_listGroups(
            team_id=self.team_id, channel_id=self.channel_id
        )
        self.assertIsNotNone(list_groups)
        # To avoid rate limiting errors
        await asyncio.sleep(10)

        remove_group = await client.admin_conversations_restrictAccess_removeGroup(
            channel_id=self.channel_id, group_id=self.idp_group_id, team_id=self.team_id
        )
        self.assertIsNotNone(remove_group)
        # To avoid rate limiting errors
        await asyncio.sleep(20)
