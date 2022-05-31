import os
import unittest

from integration_tests.env_variable_names import (
    SLACK_SDK_TEST_GRID_WORKSPACE_ADMIN_USER_TOKEN,
    SLACK_SDK_TEST_GRID_ORG_ADMIN_USER_TOKEN,
)
from slack_sdk.web import WebClient


class TestWebClient(unittest.TestCase):
    def setUp(self):
        self.org_admin_token = os.environ[SLACK_SDK_TEST_GRID_ORG_ADMIN_USER_TOKEN]
        self.client: WebClient = WebClient(token=self.org_admin_token)

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

    def test_reset(self):
        response = self.client.admin_users_session_reset(user_id=self.user_ids[0])
        self.assertIsNone(response.get("error"))

    def test_resetBulk(self):
        response = self.client.admin_users_session_resetBulk(user_ids=self.user_ids)
        self.assertIsNone(response.get("error"))

    def test_resetBulk_str(self):
        response = self.client.admin_users_session_resetBulk(user_ids=",".join(self.user_ids))
        self.assertIsNone(response.get("error"))
