import logging
import os
import time
import unittest

from integration_tests.env_variable_names import SLACK_SDK_TEST_BOT_TOKEN
from integration_tests.helpers import async_test
from slack_sdk.web import WebClient
from slack_sdk.web.async_client import AsyncWebClient


class TestWebClient(unittest.TestCase):
    """Runs integration tests with real Slack API"""

    def setUp(self):
        self.logger = logging.getLogger(__name__)
        self.bot_token = os.environ[SLACK_SDK_TEST_BOT_TOKEN]
        self.sync_client: WebClient = WebClient(token=self.bot_token)
        self.async_client: AsyncWebClient = AsyncWebClient(token=self.bot_token)

    def tearDown(self):
        pass

    def test_sync(self):
        client = self.sync_client

        # Channel canvas
        new_channel = client.conversations_create(name=f"test-{str(time.time()).replace('.', '-')}")
        channel_id = new_channel["channel"]["id"]
        channel_canvas = client.conversations_canvases_create(
            channel_id=channel_id,
            document_content={
                "type": "markdown",
                "markdown": """# My canvas
                ---
                ## Hey
                What's up?
                """,
            },
        )
        self.assertIsNone(channel_canvas.get("error"))

        # Standalone canvas
        standalone_canvas = client.canvases_create(
            title="My canvas",
            document_content={
                "type": "markdown",
                "markdown": """# My canvas
                ---
                ## Hey
                What's up?
                """,
            },
        )
        self.assertIsNone(standalone_canvas.get("error"))
        canvas_id = standalone_canvas.get("canvas_id")

        sections = client.canvases_sections_lookup(canvas_id=canvas_id, criteria={"contains_text": "Hey"})
        section_id = sections["sections"][0]["id"]

        edit = client.canvases_edit(
            canvas_id=canvas_id,
            changes=[
                {
                    "operation": "replace",
                    "section_id": section_id,
                    "document_content": {"type": "markdown", "markdown": "## Hey Hey"},
                }
            ],
        )
        self.assertIsNone(edit.get("error"))

        user_id = client.auth_test()["user_id"]
        access_set = client.canvases_access_set(
            canvas_id=canvas_id,
            access_level="write",
            user_ids=[user_id],
        )
        self.assertIsNone(access_set.get("error"))

        access_delete = client.canvases_access_delete(canvas_id=canvas_id, user_ids=[user_id])
        self.assertIsNone(access_delete.get("error"))

        delete = client.canvases_delete(canvas_id=canvas_id)
        self.assertIsNone(delete.get("error"))

    @async_test
    async def test_async(self):
        client = self.async_client

        # Channel canvas
        new_channel = await client.conversations_create(name=f"test-{str(time.time()).replace('.', '-')}")
        channel_id = new_channel["channel"]["id"]
        channel_canvas = await client.conversations_canvases_create(
            channel_id=channel_id,
            document_content={
                "type": "markdown",
                "markdown": """# My canvas
                ---
                ## Hey
                What's up?
                """,
            },
        )
        self.assertIsNone(channel_canvas.get("error"))

        # Standalone canvas
        standalone_canvas = await client.canvases_create(
            title="My canvas",
            document_content={
                "type": "markdown",
                "markdown": """# My canvas
                ---
                ## Hey
                What's up?
                """,
            },
        )
        self.assertIsNone(standalone_canvas.get("error"))
        canvas_id = standalone_canvas.get("canvas_id")

        sections = await client.canvases_sections_lookup(canvas_id=canvas_id, criteria={"contains_text": "Hey"})
        section_id = sections["sections"][0]["id"]

        edit = await client.canvases_edit(
            canvas_id=canvas_id,
            changes=[
                {
                    "operation": "replace",
                    "section_id": section_id,
                    "document_content": {"type": "markdown", "markdown": "## Hey Hey"},
                }
            ],
        )
        self.assertIsNone(edit.get("error"))

        user_id = (await client.auth_test())["user_id"]
        access_set = await client.canvases_access_set(
            canvas_id=canvas_id,
            access_level="write",
            user_ids=[user_id],
        )
        self.assertIsNone(access_set.get("error"))

        access_delete = await client.canvases_access_delete(canvas_id=canvas_id, user_ids=[user_id])
        self.assertIsNone(access_delete.get("error"))

        delete = await client.canvases_delete(canvas_id=canvas_id)
        self.assertIsNone(delete.get("error"))
