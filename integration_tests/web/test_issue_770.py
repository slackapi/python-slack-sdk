import os
import unittest
from io import BytesIO

from integration_tests.env_variable_names import (
    SLACK_SDK_TEST_BOT_TOKEN,
    SLACK_SDK_TEST_WEB_TEST_CHANNEL_ID,
)
from integration_tests.helpers import async_test
from slack_sdk.web import WebClient
from slack_sdk.web.async_client import AsyncWebClient


class TestWebClient(unittest.TestCase):
    """Runs integration tests with real Slack API

    export SLACK_SDK_TEST_BOT_TOKEN=xoxb-xxx
    export SLACK_SDK_TEST_WEB_TEST_CHANNEL_ID=C111
    python setup.py run_integration_tests --test-target integration_tests/web/test_issue_770.py

    https://github.com/slackapi/python-slack-sdk/issues/770
    """

    def setUp(self):
        self.bot_token = os.environ[SLACK_SDK_TEST_BOT_TOKEN]
        self.channel_ids = ",".join([os.environ[SLACK_SDK_TEST_WEB_TEST_CHANNEL_ID]])

    def tearDown(self):
        pass

    def test_bytes_for_file_param_bytes(self):
        client: WebClient = WebClient(token=self.bot_token)
        bytes = BytesIO(bytearray("This is a test (bytes)", "utf-8")).getvalue()
        upload = client.files_upload(file=bytes, filename="test.txt", channels=self.channel_ids)
        self.assertIsNotNone(upload)
        deletion = client.files_delete(file=upload["file"]["id"])
        self.assertIsNotNone(deletion)

    @async_test
    async def test_bytes_for_file_param_bytes_async(self):
        client: AsyncWebClient = AsyncWebClient(token=self.bot_token)
        bytes = BytesIO(bytearray("This is a test (bytes)", "utf-8")).getvalue()
        upload = await client.files_upload(file=bytes, filename="test.txt", channels=self.channel_ids)
        self.assertIsNotNone(upload)
        deletion = await client.files_delete(file=upload["file"]["id"])
        self.assertIsNotNone(deletion)
