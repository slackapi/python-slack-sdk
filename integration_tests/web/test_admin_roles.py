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

    def setUp(self):
        self.org_admin_token = os.environ[SLACK_SDK_TEST_GRID_ORG_ADMIN_USER_TOKEN]

    def tearDown(self):
        pass

    def test_sync(self):
        client: WebClient = WebClient(token=self.org_admin_token)
        list_response = client.admin_roles_listAssignments(role_ids=["Rl0A"], limit=3, sort_dir="DESC")
        self.assertGreater(len(list_response.get("role_assignments", [])), 0)
        # TODO tests for add/remove

    @async_test
    async def test_async(self):
        client: AsyncWebClient = AsyncWebClient(token=self.org_admin_token)
        list_response = await client.admin_roles_listAssignments(role_ids=["Rl0A"], limit=3, sort_dir="DESC")
        self.assertGreater(len(list_response.get("role_assignments", [])), 0)
        # TODO tests for add/remove
