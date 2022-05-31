import asyncio
import logging
import os
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
        self.idp_usergroup_id = os.environ[SLACK_SDK_TEST_GRID_IDP_USERGROUP_ID]

        if not hasattr(self, "channel_ids"):
            team_admin_token = os.environ[SLACK_SDK_TEST_GRID_WORKSPACE_ADMIN_USER_TOKEN]
            client = WebClient(token=team_admin_token)
            convs = client.conversations_list(exclude_archived=True, limit=100)
            self.channel_ids = [c["id"] for c in convs["channels"] if c["name"] == "general"]

    def tearDown(self):
        pass

    def test_sync(self):
        client = self.sync_client

        response = client.admin_users_session_list()
        self.assertIsNotNone(response["active_sessions"])

    @async_test
    async def test_async(self):
        client = self.async_client

        response = await client.admin_users_session_list()
        self.assertIsNotNone(response["active_sessions"])
