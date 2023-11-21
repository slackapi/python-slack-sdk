import asyncio
import logging
import os
import time
import unittest

from integration_tests.env_variable_names import (
    SLACK_SDK_TEST_GRID_ORG_ADMIN_USER_TOKEN,
    SLACK_SDK_TEST_GRID_TEAM_ID_2,
    SLACK_SDK_TEST_GRID_TEAM_ID,
)
from integration_tests.helpers import async_test
from slack_sdk.web import WebClient, SlackResponse
from slack_sdk.errors import SlackApiError
from slack_sdk.web.async_client import AsyncWebClient


class TestWebClient(unittest.TestCase):
    """Runs integration tests with real Slack API"""

    def setUp(self):
        self.logger = logging.getLogger(__name__)
        self.org_admin_token = os.environ[SLACK_SDK_TEST_GRID_ORG_ADMIN_USER_TOKEN]
        self.sync_client: WebClient = WebClient(token=self.org_admin_token)
        self.async_client: AsyncWebClient = AsyncWebClient(token=self.org_admin_token)

        self.team_id = os.environ[SLACK_SDK_TEST_GRID_TEAM_ID]
        self.team_id_2 = os.environ[SLACK_SDK_TEST_GRID_TEAM_ID_2]
        self.channel_name = f"test-channel-{int(round(time.time() * 1000))}"

    def tearDown(self):
        pass

    def test_sync_move(self):
        client = self.sync_client

        conv_creation = client.admin_conversations_create(
            is_private=False,
            name=self.channel_name,
            team_id=self.team_id,
        )
        self.assertIsNotNone(conv_creation)
        created_channel_id = conv_creation.data["channel_id"]

        self.assertIsNotNone(
            _get_bulk_response(
                client.admin_conversations_bulkMove,
                channel_ids=[created_channel_id],
                target_team_id=self.team_id_2,
            )
        )

    def test_sync(self):
        client = self.sync_client

        conv_creation = client.admin_conversations_create(
            is_private=False,
            name=self.channel_name,
            team_id=self.team_id,
        )
        self.assertIsNotNone(conv_creation)
        created_channel_id = conv_creation.data["channel_id"]

        self.assertIsNotNone(
            _get_bulk_response(
                client.admin_conversations_bulkArchive,
                channel_ids=[created_channel_id],
            )
        )

        self.assertIsNotNone(
            _get_bulk_response(
                client.admin_conversations_bulkDelete,
                channel_ids=[created_channel_id],
            )
        )

    @async_test
    async def test_async_move(self):
        client = self.async_client

        conv_creation = await client.admin_conversations_create(
            is_private=False,
            name=self.channel_name,
            team_id=self.team_id,
        )
        self.assertIsNotNone(conv_creation)
        created_channel_id = conv_creation.data["channel_id"]

        self.assertIsNotNone(
            await _get_async_bulk_response(
                client.admin_conversations_bulkMove,
                channel_ids=[created_channel_id],
                target_team_id=self.team_id_2,
            )
        )

    @async_test
    async def test_async(self):
        client = self.async_client

        conv_creation = await client.admin_conversations_create(
            is_private=False,
            name=self.channel_name,
            team_id=self.team_id,
        )
        self.assertIsNotNone(conv_creation)
        created_channel_id = conv_creation.data["channel_id"]

        self.assertIsNotNone(
            await _get_async_bulk_response(
                client.admin_conversations_bulkArchive,
                channel_ids=[created_channel_id],
            )
        )

        self.assertIsNotNone(
            await _get_async_bulk_response(
                client.admin_conversations_bulkDelete,
                channel_ids=[created_channel_id],
            )
        )


async def _get_async_bulk_response(method, **kwargs) -> SlackResponse:
    while True:
        try:
            return await method(**kwargs)
        except SlackApiError as e:
            if not _action_in_progress(e.response):
                raise e
            await asyncio.sleep(3)


def _get_bulk_response(method, **kwargs) -> SlackResponse:
    while True:
        try:
            return method(**kwargs)
        except SlackApiError as e:
            if not _action_in_progress(e.response):
                raise e
            time.sleep(3)


def _action_in_progress(response: SlackResponse) -> bool:
    if response.data.get("error", "") == "action_already_in_progress":
        return True
    return False
