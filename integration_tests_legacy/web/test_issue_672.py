import asyncio
import logging
import os
import unittest

from integration_tests.env_variable_names import \
    SLACK_SDK_TEST_BOT_TOKEN, \
    SLACK_SDK_TEST_WEB_TEST_CHANNEL_ID
from integration_tests.helpers import async_test
from slack import WebClient


class TestWebClient(unittest.TestCase):
    """Runs integration tests with real Slack API

    https://github.com/slackapi/python-slackclient/issues/672
    """

    def setUp(self):
        if not hasattr(self, "logger"):
            self.logger = logging.getLogger(__name__)
            self.bot_token = os.environ[SLACK_SDK_TEST_BOT_TOKEN]
            self.sync_client: WebClient = WebClient(
                token=self.bot_token,
                run_async=False,
                loop=asyncio.new_event_loop())
            self.async_client: WebClient = WebClient(token=self.bot_token, run_async=True)
            self.channel_id = os.environ[SLACK_SDK_TEST_WEB_TEST_CHANNEL_ID]

    def tearDown(self):
        pass

    def test_file_loading(self):
        client, logger, channel_ids = self.sync_client, self.logger, ",".join([self.channel_id])
        upload = client.files_upload(
            file="tests/data/日本語.txt",
            filename="日本語.txt",
            filetype="text",
            channels=channel_ids
        )
        self.assertIsNotNone(upload)
        self.assertEqual("日本語.txt", upload["file"]["name"])
        self.assertEqual("日本語の文書です。", upload["file"]["preview"])

        deletion = client.files_delete(file=upload["file"]["id"])
        self.assertIsNotNone(deletion)

    @async_test
    async def test_file_loading_async(self):
        client, logger, channel_ids = self.async_client, self.logger, ",".join([self.channel_id])
        upload = await client.files_upload(
            file="tests/data/日本語.txt",
            filename="日本語.txt",
            filetype="text",
            channels=channel_ids
        )
        logger.debug("File uploaded - %s", upload)
        self.assertIsNotNone(upload)
        self.assertEqual("日本語.txt", upload["file"]["name"])
        self.assertEqual("日本語の文書です。", upload["file"]["preview"])

        deletion = await client.files_delete(file=upload["file"]["id"])
        self.assertIsNotNone(deletion)

    def test_auto_filename_detection(self):
        client, logger, channel_ids = self.sync_client, self.logger, ",".join([self.channel_id])
        upload = client.files_upload(
            file="tests/data/日本語.txt",
            # filename="日本語.txt",
            filetype="text",
            channels=channel_ids
        )
        self.assertIsNotNone(upload)
        self.assertEqual("日本語.txt", upload["file"]["name"])
        self.assertEqual("日本語の文書です。", upload["file"]["preview"])

        deletion = client.files_delete(file=upload["file"]["id"])
        self.assertIsNotNone(deletion)

    @async_test
    async def test_auto_filename_detection_async(self):
        client, logger, channel_ids = self.async_client, self.logger, ",".join([self.channel_id])
        upload = await client.files_upload(
            file="tests/data/日本語.txt",
            # filename="日本語.txt",
            filetype="text",
            channels=channel_ids
        )
        logger.debug("File uploaded - %s", upload)
        self.assertIsNotNone(upload)
        self.assertEqual("日本語.txt", upload["file"]["name"])
        self.assertEqual("日本語の文書です。", upload["file"]["preview"])

        deletion = await client.files_delete(file=upload["file"]["id"])
        self.assertIsNotNone(deletion)
