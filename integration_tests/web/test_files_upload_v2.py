import logging
import os
import unittest
from io import BytesIO

import pytest

from integration_tests.env_variable_names import (
    SLACK_SDK_TEST_BOT_TOKEN,
    SLACK_SDK_TEST_WEB_TEST_CHANNEL_ID,
)
from integration_tests.helpers import async_test
from slack_sdk.errors import SlackRequestError
from slack_sdk.web import WebClient
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.web.legacy_client import LegacyWebClient


class TestWebClient_FilesUploads_V2(unittest.TestCase):
    """Runs integration tests with real Slack API"""

    def setUp(self):
        if not hasattr(self, "logger"):
            self.logger = logging.getLogger(__name__)
            self.bot_token = os.environ[SLACK_SDK_TEST_BOT_TOKEN]
            self.async_client: AsyncWebClient = AsyncWebClient(token=self.bot_token)
            self.sync_client: WebClient = WebClient(token=self.bot_token)
            self.legacy_client: WebClient = LegacyWebClient(token=self.bot_token)
            self.legacy_client_async: WebClient = LegacyWebClient(token=self.bot_token, run_async=True)
            self.channel_id = os.environ[SLACK_SDK_TEST_WEB_TEST_CHANNEL_ID]

    def tearDown(self):
        pass

    # -------------------------
    # file operations

    def test_uploading_text_files(self):
        client = self.sync_client
        file = __file__
        upload = client.files_upload_v2(
            channels=self.channel_id,
            file=file,
            title="Test code",
        )
        self.assertIsNotNone(upload)
        self.assertIsNotNone(upload.get("files")[0].get("id"))
        self.assertIsNotNone(upload.get("files")[0].get("title"))

    def test_uploading_bytes_io(self):
        client = self.sync_client
        upload = client.files_upload_v2(
            channels=self.channel_id,
            file=BytesIO(bytearray("This is a test!", "utf-8")),
            filename="test.txt",
            title="Test code",
        )
        self.assertIsNotNone(upload)
        self.assertIsNotNone(upload.get("files")[0].get("id"))
        self.assertIsNotNone(upload.get("files")[0].get("title"))

    def test_uploading_multiple_files(self):
        client = self.sync_client
        file = __file__
        upload = client.files_upload_v2(
            file_uploads=[
                {
                    "file": file,
                    "title": "Test code",
                },
                {
                    "content": "Hi there!",
                    "title": "Text data",
                    "filename": "hi-there.txt",
                },
            ],
            channel=self.channel_id,
            initial_comment="Here are files :wave:",
        )
        self.assertIsNotNone(upload)
        self.assertIsNotNone(upload.get("files")[0].get("id"))
        self.assertIsNotNone(upload.get("files")[0].get("title"))

    @async_test
    async def test_uploading_text_files_async(self):
        client = self.async_client
        file, filename = __file__, os.path.basename(__file__)
        upload = await client.files_upload_v2(
            channels=self.channel_id,
            title="Good Old Slack Logo",
            filename=filename,
            file=file,
        )
        self.assertIsNotNone(upload)
        self.assertIsNotNone(upload.get("files")[0].get("id"))
        self.assertIsNotNone(upload.get("files")[0].get("title"))

        deletion = await client.files_delete(file=upload["file"]["id"])
        self.assertIsNotNone(deletion)

    @async_test
    async def test_uploading_text_files_legacy_async(self):
        client = self.legacy_client_async
        file, filename = __file__, os.path.basename(__file__)
        try:
            await client.files_upload_v2(
                channels=self.channel_id,
                title="Good Old Slack Logo",
                filename=filename,
                file=file,
            )
            pytest.fail("Raising SlackRequestError is expected here")
        except SlackRequestError:
            pass

    def test_uploading_binary_files(self):
        client = self.sync_client
        current_dir = os.path.dirname(__file__)
        file = f"{current_dir}/../../tests/data/slack_logo.png"
        upload = client.files_upload_v2(
            channels=self.channel_id,
            title="Good Old Slack Logo",
            filename="slack_logo.png",
            file=file,
        )
        self.assertIsNotNone(upload)
        self.assertIsNotNone(upload.get("files")[0].get("id"))
        self.assertIsNotNone(upload.get("files")[0].get("title"))

        deletion = client.files_delete(file=upload["file"]["id"])
        self.assertIsNotNone(deletion)

    def test_uploading_binary_files_as_content(self):
        client = self.sync_client
        current_dir = os.path.dirname(__file__)
        file = f"{current_dir}/../../tests/data/slack_logo.png"
        with open(file, "rb") as f:
            content = f.read()
            upload = client.files_upload_v2(
                channels=self.channel_id,
                title="Good Old Slack Logo",
                filename="slack_logo.png",
                content=content,
            )
            self.assertIsNotNone(upload)
            self.assertIsNotNone(upload.get("files")[0].get("id"))
            self.assertIsNotNone(upload.get("files")[0].get("title"))

            deletion = client.files_delete(file=upload["file"]["id"])
            self.assertIsNotNone(deletion)

    @async_test
    async def test_uploading_binary_files_async(self):
        client = self.async_client
        current_dir = os.path.dirname(__file__)
        file = f"{current_dir}/../../tests/data/slack_logo.png"
        upload = await client.files_upload_v2(
            channels=self.channel_id,
            title="Good Old Slack Logo",
            filename="slack_logo.png",
            file=file,
        )
        self.assertIsNotNone(upload)
        self.assertIsNotNone(upload.get("files")[0].get("id"))
        self.assertIsNotNone(upload.get("files")[0].get("title"))

        deletion = await client.files_delete(file=upload["file"]["id"])
        self.assertIsNotNone(deletion)

    def test_uploading_file_with_token_param(self):
        client = WebClient()
        current_dir = os.path.dirname(__file__)
        file = f"{current_dir}/../../tests/data/slack_logo.png"
        upload = client.files_upload_v2(
            token=self.bot_token,
            channels=self.channel_id,
            title="Good Old Slack Logo",
            filename="slack_logo.png",
            file=file,
        )
        self.assertIsNotNone(upload)
        self.assertIsNotNone(upload.get("files")[0].get("id"))
        self.assertIsNotNone(upload.get("files")[0].get("title"))

        deletion = client.files_delete(
            token=self.bot_token,
            file=upload["file"]["id"],
        )
        self.assertIsNotNone(deletion)

    @async_test
    async def test_uploading_file_with_token_param_async(self):
        client = AsyncWebClient()
        current_dir = os.path.dirname(__file__)
        file = f"{current_dir}/../../tests/data/slack_logo.png"
        upload = await client.files_upload_v2(
            token=self.bot_token,
            channels=self.channel_id,
            title="Good Old Slack Logo",
            filename="slack_logo.png",
            file=file,
        )
        self.assertIsNotNone(upload)
        self.assertIsNotNone(upload.get("files")[0].get("id"))
        self.assertIsNotNone(upload.get("files")[0].get("title"))

        deletion = await client.files_delete(
            token=self.bot_token,
            file=upload["file"]["id"],
        )
        self.assertIsNotNone(deletion)
