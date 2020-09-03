import asyncio
import logging
import os
import time
import unittest

from integration_tests.env_variable_names import SLACK_SDK_TEST_GRID_WORKSPACE_ADMIN_USER_TOKEN, \
    SLACK_SDK_TEST_GRID_ORG_ADMIN_USER_TOKEN, \
    SLACK_SDK_TEST_GRID_IDP_USERGROUP_ID, SLACK_SDK_TEST_GRID_TEAM_ID, SLACK_SDK_TEST_WEB_TEST_USER_ID
from integration_tests.helpers import async_test
from slack import WebClient


class TestWebClient(unittest.TestCase):
    """Runs integration tests with real Slack API"""

    def setUp(self):
        self.logger = logging.getLogger(__name__)
        self.org_admin_token = os.environ[SLACK_SDK_TEST_GRID_ORG_ADMIN_USER_TOKEN]
        self.sync_client: WebClient = WebClient(
            token=self.org_admin_token,
            run_async=False,
            loop=asyncio.new_event_loop()
        )
        self.async_client: WebClient = WebClient(token=self.org_admin_token, run_async=True)

        self.team_id = os.environ[SLACK_SDK_TEST_GRID_TEAM_ID]
        self.idp_group_id = os.environ[SLACK_SDK_TEST_GRID_IDP_USERGROUP_ID]
        self.user_id = os.environ[SLACK_SDK_TEST_WEB_TEST_USER_ID]
        self.channel_name = f'my-channel-{int(round(time.time() * 1000))}'
        self.channel_rename = f'my-renamed-channel-{int(round(time.time() * 1000))}'

        if not hasattr(self, "channel_id"):
            team_admin_token = os.environ[SLACK_SDK_TEST_GRID_WORKSPACE_ADMIN_USER_TOKEN]
            client = WebClient(token=team_admin_token)
            # Only fetching private channels since admin.conversations.restrictAccess methods do not work for public channels
            convs = client.conversations_list(exclude_archived=True, limit=100, types="private_channel")
            self.channel_id = next((c["id"] for c in convs["channels"] if c["name"] != "general"), None)
            if self.channel_id is None:
                millis = int(round(time.time() * 1000))
                channel_name = f"private-test-channel-{millis}"
                self.channel_id = client.conversations_create(
                    name=channel_name,
                    is_private=True,
                )["channel"]["id"]

    def tearDown(self):
        pass

    def test_sync(self):
        # time.sleep(seconds) are included to avoid rate limiting errors
        client = self.sync_client

        add_group = client.admin_conversations_restrictAccess_addGroup(
            channel_id=self.channel_id,
            group_id=self.idp_group_id,
            team_id=self.team_id
        )
        self.assertIsNotNone(add_group)
        # To avoid rate limiting errors
        time.sleep(10)

        list_groups = client.admin_conversations_restrictAccess_listGroups(
            team_id=self.team_id,
            channel_id=self.channel_id
        )
        self.assertIsNotNone(list_groups)
        # To avoid rate limiting errors
        time.sleep(10)

        remove_group = client.admin_conversations_restrictAccess_removeGroup(
            channel_id=self.channel_id,
            group_id=self.idp_group_id,
            team_id=self.team_id
        )
        self.assertIsNotNone(remove_group)
        # To avoid rate limiting errors
        time.sleep(20)

        conversations_create = client.admin_conversations_create(is_private=False, name=self.channel_name)
        self.assertIsNotNone(conversations_create)
        created_channel_id = conversations_create.data["channel_id"]

        self.assertIsNotNone(client.admin_conversations_invite(channel_id=created_channel_id, user_ids=[self.user_id]))
        self.assertIsNotNone(client.admin_conversations_archive(channel_id=created_channel_id))
        self.assertIsNotNone(client.admin_conversations_unarchive(channel_id=created_channel_id))
        self.assertIsNotNone(client.admin_conversations_rename(channel_id=created_channel_id, name=self.channel_rename))
        self.assertIsNotNone(client.admin_conversations_search())

        self.assertIsNotNone(client.admin_conversations_getConversationPrefs(channel_id=created_channel_id))
        self.assertIsNotNone(client.admin_conversations_setConversationPrefs(channel_id=created_channel_id, prefs={}))

        self.assertIsNotNone(client.admin_conversations_getTeams(channel_id=created_channel_id))
        self.assertIsNotNone(client.admin_conversations_setTeams(channel_id=created_channel_id, org_channel=True))
        self.assertIsNotNone(client.admin_conversations_disconnectShared(channel_id=created_channel_id))

        self.assertIsNotNone(client.admin_conversations_convertToPrivate(channel_id=created_channel_id))
        self.assertIsNotNone(client.admin_conversations_delete(channel_id=created_channel_id))

    @async_test
    async def test_async(self):
        # await asyncio.sleep(seconds) are included to avoid rate limiting errors

        client = self.async_client

        add_group = await client.admin_conversations_restrictAccess_addGroup(
            channel_id=self.channel_id,
            group_id=self.idp_group_id,
            team_id=self.team_id
        )
        self.assertIsNotNone(add_group)
        # To avoid rate limiting errors
        await asyncio.sleep(10)

        list_groups = await client.admin_conversations_restrictAccess_listGroups(
            team_id=self.team_id,
            channel_id=self.channel_id
        )
        self.assertIsNotNone(list_groups)
        # To avoid rate limiting errors
        await asyncio.sleep(10)

        remove_group = await client.admin_conversations_restrictAccess_removeGroup(
            channel_id=self.channel_id,
            group_id=self.idp_group_id,
            team_id=self.team_id
        )
        self.assertIsNotNone(remove_group)
        # To avoid rate limiting errors
        await asyncio.sleep(20)

        conversations_create = await client.admin_conversations_create(is_private=False, name=self.channel_name)
        self.assertIsNotNone(conversations_create)
        created_channel_id = conversations_create.data["channel_id"]

        self.assertIsNotNone(
            await client.admin_conversations_invite(channel_id=created_channel_id, user_ids=[self.user_id]))
        self.assertIsNotNone(await client.admin_conversations_archive(channel_id=created_channel_id))
        self.assertIsNotNone(await client.admin_conversations_unarchive(channel_id=created_channel_id))
        self.assertIsNotNone(await client.admin_conversations_rename(
            channel_id=created_channel_id,
            name=self.channel_rename
        ))
        self.assertIsNotNone(await client.admin_conversations_search())

        self.assertIsNotNone(await client.admin_conversations_getConversationPrefs(channel_id=created_channel_id))
        self.assertIsNotNone(await client.admin_conversations_setConversationPrefs(
            channel_id=created_channel_id,
            prefs={}
        ))

        self.assertIsNotNone(await client.admin_conversations_getTeams(channel_id=created_channel_id))
        self.assertIsNotNone(await client.admin_conversations_setTeams(channel_id=created_channel_id, org_channel=True))
        self.assertIsNotNone(await client.admin_conversations_disconnectShared(channel_id=created_channel_id))

        self.assertIsNotNone(await client.admin_conversations_convertToPrivate(channel_id=created_channel_id))
        self.assertIsNotNone(await client.admin_conversations_delete(channel_id=created_channel_id))
