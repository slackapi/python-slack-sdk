import asyncio
import io
import logging
import os
import unittest

from integration_tests.env_variable_names import SLACK_SDK_TEST_BOT_TOKEN
from integration_tests.helpers import async_test
from slack_sdk.web import WebClient
from slack_sdk.web.async_client import AsyncWebClient


class TestWebClient(unittest.TestCase):
    """Runs integration tests with real Slack API

    https://github.com/slackapi/python-slack-sdk/issues/809
    """

    def setUp(self):
        self.logger = logging.getLogger(__name__)
        self.bot_token = os.environ[SLACK_SDK_TEST_BOT_TOKEN]
        self.sync_client: WebClient = WebClient(token=self.bot_token)
        self.async_client: AsyncWebClient = AsyncWebClient(token=self.bot_token)

    def tearDown(self):
        pass

    def test_issue_809(self):
        client = self.sync_client
        buff = io.BytesIO(b"here is my data but not sure what is wrong.......")
        buff.seek(0)
        upload = client.files_upload(file=buff)
        self.assertIsNotNone(upload)

    @async_test
    async def test_issue_809_async(self):
        client = self.async_client
        buff = io.BytesIO(b"here is my data but not sure what is wrong.......")
        buff.seek(0)
        upload = await client.files_upload(file=buff)
        self.assertIsNotNone(upload)
