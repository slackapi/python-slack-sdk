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
from slack import WebClient


class TestWebClient(unittest.TestCase):
    """Runs integration tests with real Slack API"""

    def setUp(self):
        self.logger = logging.getLogger(__name__)
        self.org_admin_token = os.environ[SLACK_SDK_TEST_GRID_ORG_ADMIN_USER_TOKEN]
        self.sync_client: WebClient = WebClient(
            token=self.org_admin_token, run_async=False, loop=asyncio.new_event_loop()
        )
        self.async_client: WebClient = WebClient(
            token=self.org_admin_token, run_async=True
        )

    def tearDown(self):
        pass

    def test_sync(self):
        client = self.sync_client

        create_response = client.admin_barriers_create(
            barriered_from_usergroup_ids=["1", "2", "3"],
            primary_usergroup_id=4,
            restricted_subjects=["im", "mpim"],
        )
        self.assertIsNotNone(create_response["barrier"])

        barrier_id = create_response["barrier"]["id"]

        update_response = client.admin_barriers_update(
            barrier_id=barrier_id,
            barriered_from_usergroup_ids=["4", "5", "6"],
            primary_usergroup_id=5,
            restricted_subjects=["im"],
        )
        self.assertIsNotNone(update_response["barrier"])

        list_response = client.admin_barriers_list()
        self.assertIsNotNone(list_response["barriers"])

        delete_response = client.admin_barriers_delete(barrier_id=barrier_id)
        self.assertIsNotNone(delete_response)

    @async_test
    async def test_async(self):
        client = self.async_client

        create_response = await client.admin_barriers_create(
            barriered_from_usergroup_ids=["1", "2", "3"],
            primary_usergroup_id=4,
            restricted_subjects=["im", "mpim"],
        )
        self.assertIsNotNone(create_response["barrier"])

        barrier_id = create_response["barrier"]["id"]

        update_response = await client.admin_barriers_update(
            barrier_id=barrier_id,
            barriered_from_usergroup_ids=["4", "5", "6"],
            primary_usergroup_id=5,
            restricted_subjects=["im"],
        )
        self.assertIsNotNone(update_response["barrier"])

        list_response = await client.admin_barriers_list()
        self.assertIsNotNone(list_response["barriers"])

        delete_response = await client.admin_barriers_delete(barrier_id=barrier_id)
        self.assertIsNotNone(delete_response)
