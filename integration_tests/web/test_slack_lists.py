import logging
import os
import unittest

from integration_tests.env_variable_names import (
    SLACK_SDK_TEST_BOT_TOKEN,
)
from integration_tests.helpers import async_test
from slack_sdk.web import WebClient
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.models.blocks import RichTextBlock
from slack_sdk.models.blocks.block_elements import RichTextSection, RichTextText


class TestSlackLists(unittest.TestCase):
    """Runs integration tests with real Slack API testing the slackLists.* APIs"""

    def setUp(self):
        if not hasattr(self, "logger"):
            self.logger = logging.getLogger(__name__)
            self.bot_token = os.environ[SLACK_SDK_TEST_BOT_TOKEN]
            self.async_client: AsyncWebClient = AsyncWebClient(token=self.bot_token)
            self.sync_client: WebClient = WebClient(token=self.bot_token)

    def tearDown(self):
        pass

    def test_create_list_with_dicts(self):
        """Test creating a list with description_blocks as dicts"""
        client = self.sync_client

        create_response = client.slackLists_create(
            name="Test Sales Pipeline",
            description_blocks=[
                {
                    "type": "rich_text",
                    "elements": [
                        {
                            "type": "rich_text_section",
                            "elements": [{"type": "text", "text": "This is a test list for integration testing"}],
                        }
                    ],
                }
            ],
            schema=[
                {"key": "deal_name", "name": "Deal Name", "type": "text", "is_primary_column": True},
                {"key": "amount", "name": "Amount", "type": "number", "options": {"format": "currency", "precision": 2}},
            ],
        )

        self.assertIsNotNone(create_response)
        self.assertTrue(create_response["ok"])
        self.assertIn("list", create_response)
        list_id = create_response["list"]["id"]
        self.logger.info(f"✓ Created list with ID: {list_id}")

    def test_create_list_with_rich_text_blocks(self):
        """Test creating a list with RichTextBlock objects"""
        client = self.sync_client

        create_response = client.slackLists_create(
            name="Test List with Rich Text Blocks",
            description_blocks=[
                RichTextBlock(
                    elements=[RichTextSection(elements=[RichTextText(text="Created with RichTextBlock objects!")])]
                )
            ],
            schema=[{"key": "task_name", "name": "Task", "type": "text", "is_primary_column": True}],
        )

        self.assertIsNotNone(create_response)
        self.assertTrue(create_response["ok"])
        list_id = create_response["list"]["id"]
        self.logger.info(f"✓ Created list with RichTextBlocks, ID: {list_id}")

    @async_test
    async def test_create_list_async(self):
        """Test creating a list with async client"""
        client = self.async_client

        create_response = await client.slackLists_create(
            name="Async Test List", schema=[{"key": "item_name", "name": "Item", "type": "text", "is_primary_column": True}]
        )

        self.assertIsNotNone(create_response)
        self.assertTrue(create_response["ok"])
        list_id = create_response["list"]["id"]
        self.logger.info(f"✓ Created list asynchronously, ID: {list_id}")
