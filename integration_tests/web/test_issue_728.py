import os
import unittest

from integration_tests.env_variable_names import (
    SLACK_SDK_TEST_BOT_TOKEN,
    SLACK_SDK_TEST_WEB_TEST_CHANNEL_ID,
)
from integration_tests.helpers import async_test
from slack_sdk.web import WebClient
from slack_sdk.web.async_client import AsyncWebClient


class TestWebClient(unittest.TestCase):
    """Runs integration tests with real Slack API

    https://github.com/slackapi/python-slack-sdk/issues/728
    """

    def setUp(self):
        self.bot_token = os.environ[SLACK_SDK_TEST_BOT_TOKEN]
        self.channel_ids = ",".join([os.environ[SLACK_SDK_TEST_WEB_TEST_CHANNEL_ID]])

    def tearDown(self):
        pass

    def test_bytes_for_file_param(self):
        client: WebClient = WebClient(token=self.bot_token)
        bytes = bytearray("This is a test", "utf-8")
        upload = client.files_upload(file=bytes, filename="test.txt", channels=self.channel_ids)
        self.assertIsNotNone(upload)
        deletion = client.files_delete(file=upload["file"]["id"])
        self.assertIsNotNone(deletion)

    @async_test
    async def test_bytes_for_file_param_async(self):
        client: AsyncWebClient = AsyncWebClient(token=self.bot_token)
        bytes = bytearray("This is a test", "utf-8")
        upload = await client.files_upload(file=bytes, filename="test.txt", channels=self.channel_ids)
        self.assertIsNotNone(upload)
        deletion = await client.files_delete(file=upload["file"]["id"])
        self.assertIsNotNone(deletion)
