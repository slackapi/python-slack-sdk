import logging
import os
import unittest

from integration_tests.env_variable_names import (
    SLACK_SDK_TEST_GRID_ORG_ADMIN_USER_TOKEN,
    SLACK_SDK_TEST_GRID_IDP_USERGROUP_ID,
    SLACK_SDK_TEST_GRID_IDP_USERGROUP_ID_2,
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

        self.idp_usergroup_id1 = os.environ[SLACK_SDK_TEST_GRID_IDP_USERGROUP_ID]
        self.idp_usergroup_id2 = os.environ[SLACK_SDK_TEST_GRID_IDP_USERGROUP_ID_2]

    def tearDown(self):
        pass

    def test_sync(self):
        client = self.sync_client

        list = client.admin_barriers_list(limit=1000)
        self.assertIsNotNone(list)

        for barrier in list["barriers"]:
            client.admin_barriers_delete(barrier_id=barrier["id"])

        creation = client.admin_barriers_create(
            primary_usergroup_id=self.idp_usergroup_id1,
            barriered_from_usergroup_ids=[self.idp_usergroup_id2],
            restricted_subjects=["call", "im", "mpim"],
        )
        self.assertIsNotNone(creation)

        modification = client.admin_barriers_update(
            barrier_id=creation["barrier"]["id"],
            primary_usergroup_id=self.idp_usergroup_id2,
            barriered_from_usergroup_ids=[self.idp_usergroup_id1],
            restricted_subjects=["call", "im", "mpim"],
        )
        self.assertIsNotNone(modification)

    @async_test
    async def test_async(self):
        client = self.async_client

        list = await client.admin_barriers_list(limit=1000)
        self.assertIsNotNone(list)

        for barrier in list["barriers"]:
            await client.admin_barriers_delete(barrier_id=barrier["id"])

        creation = await client.admin_barriers_create(
            primary_usergroup_id=self.idp_usergroup_id1,
            barriered_from_usergroup_ids=[self.idp_usergroup_id2],
            restricted_subjects=["call", "im", "mpim"],
        )
        self.assertIsNotNone(creation)

        modification = await client.admin_barriers_update(
            barrier_id=creation["barrier"]["id"],
            primary_usergroup_id=self.idp_usergroup_id2,
            barriered_from_usergroup_ids=[self.idp_usergroup_id1],
            restricted_subjects=["call", "im", "mpim"],
        )
        self.assertIsNotNone(modification)
