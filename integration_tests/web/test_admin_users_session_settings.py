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

        if not hasattr(self, "user_ids"):
            team_admin_token = os.environ[SLACK_SDK_TEST_GRID_WORKSPACE_ADMIN_USER_TOKEN]
            client = WebClient(token=team_admin_token)
            users = client.users_list(exclude_archived=True, limit=50)
            self.user_ids = [
                u["id"]
                for u in users["members"]
                if not u["is_bot"]
                and not u["deleted"]
                and not u["is_app_user"]
                and not u["is_owner"]
                and not u.get("is_stranger")
            ][:3]

    def tearDown(self):
        pass

    def test_sync(self):
        client = self.sync_client

        response = client.admin_users_session_getSettings(user_ids=self.user_ids)
        self.assertIsNotNone(response["session_settings"])
        client.admin_users_session_setSettings(user_ids=self.user_ids, duration=60 * 60 * 24 * 30)
        client.admin_users_session_clearSettings(user_ids=self.user_ids)

    @async_test
    async def test_async(self):
        client = self.async_client

        response = await client.admin_users_session_getSettings(user_ids=self.user_ids)
        self.assertIsNotNone(response["session_settings"])
        await client.admin_users_session_setSettings(user_ids=self.user_ids, duration=60 * 60 * 24 * 30)
        await client.admin_users_session_clearSettings(user_ids=self.user_ids)
