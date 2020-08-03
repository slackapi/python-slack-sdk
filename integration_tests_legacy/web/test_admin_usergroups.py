import asyncio
import logging
import os
import unittest

from integration_tests.env_variable_names import SLACK_SDK_TEST_GRID_WORKSPACE_ADMIN_USER_TOKEN, \
    SLACK_SDK_TEST_GRID_ORG_ADMIN_USER_TOKEN, \
    SLACK_SDK_TEST_GRID_IDP_USERGROUP_ID, SLACK_SDK_TEST_GRID_TEAM_ID
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
        self.idp_usergroup_id = os.environ[SLACK_SDK_TEST_GRID_IDP_USERGROUP_ID]

        if not hasattr(self, "channel_ids"):
            team_admin_token = os.environ[SLACK_SDK_TEST_GRID_WORKSPACE_ADMIN_USER_TOKEN]
            client = WebClient(token=team_admin_token, run_async=False, loop=asyncio.new_event_loop())
            convs = client.conversations_list(exclude_archived=True, limit=100)
            self.channel_ids = [c["id"] for c in convs["channels"] if c["name"] == "general"]

    def tearDown(self):
        pass

    def test_sync(self):
        client = self.sync_client

        list_channels = client.admin_usergroups_listChannels(
            team_id=self.team_id,
            usergroup_id=self.idp_usergroup_id,
        )
        self.assertIsNotNone(list_channels)

        add_teams = client.admin_usergroups_addTeams(
            usergroup_id=self.idp_usergroup_id,
            team_ids=self.team_id,
        )
        self.assertIsNotNone(add_teams)

        add_channels = client.admin_usergroups_addChannels(
            team_id=self.team_id,
            usergroup_id=self.idp_usergroup_id,
            channel_ids=self.channel_ids,
        )
        self.assertIsNotNone(add_channels)

        remove_channels = client.admin_usergroups_removeChannels(
            usergroup_id=self.idp_usergroup_id,
            channel_ids=self.channel_ids,
        )
        self.assertIsNotNone(remove_channels)

    @async_test
    async def test_async(self):
        client = self.async_client

        list_channels = await client.admin_usergroups_listChannels(
            team_id=self.team_id,
            usergroup_id=self.idp_usergroup_id,
        )
        self.assertIsNotNone(list_channels)

        add_teams = await client.admin_usergroups_addTeams(
            usergroup_id=self.idp_usergroup_id,
            team_ids=self.team_id,
        )
        self.assertIsNotNone(add_teams)

        add_channels = await client.admin_usergroups_addChannels(
            team_id=self.team_id,
            usergroup_id=self.idp_usergroup_id,
            channel_ids=self.channel_ids,
        )
        self.assertIsNotNone(add_channels)

        remove_channels = await client.admin_usergroups_removeChannels(
            usergroup_id=self.idp_usergroup_id,
            channel_ids=self.channel_ids,
        )
        self.assertIsNotNone(remove_channels)
