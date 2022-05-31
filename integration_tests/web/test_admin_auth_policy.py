import logging
import os
import unittest

from integration_tests.env_variable_names import (
    SLACK_SDK_TEST_GRID_ORG_ADMIN_USER_TOKEN,
    SLACK_SDK_TEST_GRID_USER_ID_ADMIN_AUTH,
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
        self.user_ids = [os.environ[SLACK_SDK_TEST_GRID_USER_ID_ADMIN_AUTH]]

    def tearDown(self):
        pass

    def test_sync(self):
        client = self.sync_client

        list = client.admin_auth_policy_getEntities(policy_name="email_password", limit=3)
        self.assertIsNotNone(list)

        assignment = client.admin_auth_policy_assignEntities(
            entity_ids=self.user_ids,
            policy_name="email_password",
            entity_type="USER",
        )
        self.assertIsNotNone(assignment)
        self.assertEqual(list["entity_total_count"] + 1, assignment["entity_total_count"])

        removal = client.admin_auth_policy_removeEntities(
            entity_ids=self.user_ids,
            policy_name="email_password",
            entity_type="USER",
        )
        self.assertIsNotNone(removal)
        self.assertEqual(list["entity_total_count"], removal["entity_total_count"])

    @async_test
    async def test_async(self):
        client = self.async_client

        list = await client.admin_auth_policy_getEntities(policy_name="email_password", limit=3)
        self.assertIsNotNone(list)

        assignment = await client.admin_auth_policy_assignEntities(
            entity_ids=self.user_ids,
            policy_name="email_password",
            entity_type="USER",
        )
        self.assertIsNotNone(assignment)
        self.assertEqual(list["entity_total_count"] + 1, assignment["entity_total_count"])

        removal = await client.admin_auth_policy_removeEntities(
            entity_ids=self.user_ids,
            policy_name="email_password",
            entity_type="USER",
        )
        self.assertIsNotNone(removal)
        self.assertEqual(list["entity_total_count"], removal["entity_total_count"])
