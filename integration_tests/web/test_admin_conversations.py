import asyncio
import logging
import os
import time
import unittest

from integration_tests.env_variable_names import (
    SLACK_SDK_TEST_GRID_ORG_ADMIN_USER_TOKEN,
    SLACK_SDK_TEST_GRID_IDP_USERGROUP_ID,
    SLACK_SDK_TEST_GRID_TEAM_ID,
    SLACK_SDK_TEST_GRID_USER_ID,
)
from integration_tests.helpers import async_test
from slack_sdk.web import WebClient
from slack_sdk.web.async_client import AsyncWebClient


class TestWebClient(unittest.TestCase):
    """Runs integration tests with real Slack API"""

    # TODO: admin_conversations_disconnectShared - not_allowed_token_type
    # TODO: admin_conversations_ekm_listOriginalConnectedChannelInfo - enable the feature

    def setUp(self):
        self.logger = logging.getLogger(__name__)
        self.org_admin_token = os.environ[SLACK_SDK_TEST_GRID_ORG_ADMIN_USER_TOKEN]
        self.sync_client: WebClient = WebClient(token=self.org_admin_token)
        self.async_client: AsyncWebClient = AsyncWebClient(token=self.org_admin_token)

        self.team_id = os.environ[SLACK_SDK_TEST_GRID_TEAM_ID]
        self.idp_group_id = os.environ[SLACK_SDK_TEST_GRID_IDP_USERGROUP_ID]
        self.user_id = os.environ[SLACK_SDK_TEST_GRID_USER_ID]
        self.channel_name = f"test-channel-{int(round(time.time() * 1000))}"
        self.channel_rename = f"test-channel-renamed-{int(round(time.time() * 1000))}"

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

        self.assertIsNotNone(client.admin_conversations_lookup(last_message_activity_before=100, team_ids=[self.team_id]))

        self.assertIsNotNone(
            client.admin_conversations_invite(
                channel_id=created_channel_id,
                user_ids=[self.user_id],
            )
        )
        self.assertIsNotNone(
            client.admin_conversations_archive(
                channel_id=created_channel_id,
            )
        )
        self.assertIsNotNone(
            client.admin_conversations_unarchive(
                channel_id=created_channel_id,
            )
        )
        self.assertIsNotNone(
            client.admin_conversations_rename(
                channel_id=created_channel_id,
                name=self.channel_rename,
            )
        )
        search_result = client.admin_conversations_search(
            limit=1,
            sort="member_count",
            sort_dir="desc",
        )
        self.assertIsNotNone(search_result.data["next_cursor"])
        self.assertIsNotNone(search_result.data["conversations"])

        self.assertIsNotNone(
            client.admin_conversations_getConversationPrefs(
                channel_id=created_channel_id,
            )
        )
        self.assertIsNotNone(
            client.admin_conversations_setConversationPrefs(
                channel_id=created_channel_id,
                prefs={},
            )
        )

        self.assertIsNotNone(
            client.admin_conversations_getTeams(
                channel_id=created_channel_id,
            )
        )
        self.assertIsNotNone(
            client.admin_conversations_setTeams(
                team_id=self.team_id,
                channel_id=created_channel_id,
                org_channel=True,
            )
        )
        time.sleep(2)  # To avoid channel_not_found
        self.assertIsNotNone(
            client.admin_conversations_convertToPrivate(
                channel_id=created_channel_id,
            )
        )
        time.sleep(2)  # To avoid internal_error
        self.assertIsNotNone(
            client.admin_conversations_convertToPublic(
                channel_id=created_channel_id,
            )
        )
        time.sleep(2)  # To avoid internal_error
        self.assertIsNotNone(
            client.admin_conversations_archive(
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
            await client.admin_conversations_lookup(last_message_activity_before=100, team_ids=[self.team_id])
        )

        self.assertIsNotNone(
            await client.admin_conversations_invite(
                channel_id=created_channel_id,
                user_ids=[self.user_id],
            )
        )
        self.assertIsNotNone(
            await client.admin_conversations_archive(
                channel_id=created_channel_id,
            )
        )
        self.assertIsNotNone(
            await client.admin_conversations_unarchive(
                channel_id=created_channel_id,
            )
        )
        self.assertIsNotNone(
            await client.admin_conversations_rename(
                channel_id=created_channel_id,
                name=self.channel_rename,
            )
        )
        self.assertIsNotNone(await client.admin_conversations_search())

        self.assertIsNotNone(
            await client.admin_conversations_getConversationPrefs(
                channel_id=created_channel_id,
            )
        )
        self.assertIsNotNone(
            await client.admin_conversations_setConversationPrefs(
                channel_id=created_channel_id,
                prefs={},
            )
        )

        self.assertIsNotNone(
            await client.admin_conversations_getTeams(
                channel_id=created_channel_id,
            )
        )
        self.assertIsNotNone(
            await client.admin_conversations_setTeams(
                team_id=self.team_id,
                channel_id=created_channel_id,
                org_channel=True,
            )
        )
        await asyncio.sleep(2)  # To avoid channel_not_found
        self.assertIsNotNone(
            await client.admin_conversations_convertToPrivate(
                channel_id=created_channel_id,
            )
        )
        await asyncio.sleep(2)  # To avoid internal_error
        self.assertIsNotNone(
            await client.admin_conversations_convertToPublic(
                channel_id=created_channel_id,
            )
        )
        await asyncio.sleep(2)  # To avoid internal_error
        self.assertIsNotNone(
            await client.admin_conversations_archive(
                channel_id=created_channel_id,
            )
        )
        await asyncio.sleep(2)  # To avoid internal_error
        self.assertIsNotNone(
            await client.admin_conversations_delete(
                channel_id=created_channel_id,
            )
        )
