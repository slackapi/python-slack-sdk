import logging
import os
import unittest

from integration_tests.env_variable_names import (
    SLACK_SDK_TEST_GRID_ORG_ADMIN_USER_TOKEN,
)
from integration_tests.helpers import async_test
from slack_sdk.errors import SlackApiError
from slack_sdk.web.legacy_client import LegacyWebClient
from slack_sdk.web import WebClient
from slack_sdk.web.async_client import AsyncWebClient


class TestWebClient(unittest.TestCase):
    """Runs integration tests with real Slack API"""

    def setUp(self):
        self.logger = logging.getLogger(__name__)
        self.org_admin_token = os.environ[SLACK_SDK_TEST_GRID_ORG_ADMIN_USER_TOKEN]
        self.legacy_client: LegacyWebClient = LegacyWebClient(token=self.org_admin_token)
        self.sync_client: WebClient = WebClient(token=self.org_admin_token)
        self.async_client: WebClient = AsyncWebClient(token=self.org_admin_token)

    def tearDown(self):
        pass

    def test_sync(self):
        client = self.sync_client

        response = client.admin_analytics_getFile(date="2022-10-20", type="member")
        self.assertTrue(isinstance(response.data, bytes))
        self.assertIsNotNone(response.data)

    def test_sync_error(self):
        client = self.sync_client

        try:
            client.admin_analytics_getFile(date="2035-12-31", type="member")
        except SlackApiError as e:
            self.assertFalse(e.response["ok"])
            self.assertEqual("file_not_yet_available", e.response["error"])

    def test_sync_public_channel(self):
        client = self.sync_client

        response = client.admin_analytics_getFile(date="2022-10-20", type="public_channel")
        self.assertTrue(isinstance(response.data, bytes))
        self.assertIsNotNone(response.data)

    def test_sync_public_channel_medata_only(self):
        client = self.sync_client

        response = client.admin_analytics_getFile(type="public_channel", metadata_only=True)
        self.assertTrue(isinstance(response.data, bytes))
        self.assertIsNotNone(response.data)

    @async_test
    async def test_async(self):
        client = self.async_client

        response = await client.admin_analytics_getFile(date="2022-10-20", type="member")
        self.assertTrue(isinstance(response.data, bytes))
        self.assertIsNotNone(response.data)

    @async_test
    async def test_async_error(self):
        client = self.async_client

        try:
            await client.admin_analytics_getFile(date="2035-12-31", type="member")
        except SlackApiError as e:
            self.assertFalse(e.response["ok"])
            self.assertEqual("file_not_yet_available", e.response["error"])

    @async_test
    async def test_async_public_channel(self):
        client = self.async_client

        response = await client.admin_analytics_getFile(date="2022-10-20", type="public_channel")
        self.assertTrue(isinstance(response.data, bytes))
        self.assertIsNotNone(response.data)

    @async_test
    async def test_async_public_channel_metadata_only(self):
        client = self.async_client

        response = await client.admin_analytics_getFile(
            type="public_channel",
            metadata_only=True,
        )
        self.assertTrue(isinstance(response.data, bytes))
        self.assertIsNotNone(response.data)

    def test_legacy(self):
        client = self.legacy_client

        response = client.admin_analytics_getFile(date="2022-10-20", type="member")
        self.assertTrue(isinstance(response.data, bytes))
        self.assertIsNotNone(response.data)

    def test_legacy_public_channel(self):
        client = self.legacy_client

        response = client.admin_analytics_getFile(date="2022-10-20", type="public_channel")
        self.assertTrue(isinstance(response.data, bytes))
        self.assertIsNotNone(response.data)

    def test_legacy_public_channel_metadata_only(self):
        client = self.legacy_client

        response = client.admin_analytics_getFile(type="public_channel", metadata_only=True)
        self.assertTrue(isinstance(response.data, bytes))
        self.assertIsNotNone(response.data)
