import asyncio
import io
import logging
import os
import unittest

from integration_tests.env_variable_names import SLACK_SDK_TEST_BOT_TOKEN
from integration_tests.helpers import async_test
from slack import WebClient


class TestWebClient(unittest.TestCase):
    """Runs integration tests with real Slack API

    https://github.com/slackapi/python-slackclient/issues/670
    """

    def setUp(self):
        self.logger = logging.getLogger(__name__)
        self.bot_token = os.environ[SLACK_SDK_TEST_BOT_TOKEN]
        self.sync_client: WebClient = WebClient(token=self.bot_token, run_async=False, loop=asyncio.new_event_loop())
        self.async_client: WebClient = WebClient(token=self.bot_token, run_async=True)

    def tearDown(self):
        pass

    def test_issue_670(self):
        client = self.sync_client
        buff = io.BytesIO(b'here is my data but not sure what is wrong.......')
        buff.seek(0)
        upload = client.files_upload(
            file=buff,
            filename="output.text",
            filetype="text",
            title=None,
        )
        self.assertIsNotNone(upload)

    @async_test
    async def test_issue_670_async(self):
        client = self.async_client
        buff = io.BytesIO(b'here is my data but not sure what is wrong.......')
        buff.seek(0)
        upload = await client.files_upload(
            file=buff,
            filename="output.text",
            filetype="text",
            title=None,
        )
        self.assertIsNotNone(upload)
