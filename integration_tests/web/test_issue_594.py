import asyncio
import logging
import os
import unittest
from uuid import uuid4

from integration_tests.env_variable_names import (
    SLACK_SDK_TEST_BOT_TOKEN,
    SLACK_SDK_TEST_WEB_TEST_CHANNEL_ID,
    SLACK_SDK_TEST_WEB_TEST_USER_ID,
)
from slack_sdk.web import WebClient
from slack_sdk.web.async_client import AsyncWebClient


class TestWebClient(unittest.TestCase):
    """Runs integration tests with real Slack API

    https://github.com/slackapi/python-slack-sdk/issues/594
    """

    def setUp(self):
        self.logger = logging.getLogger(__name__)
        self.bot_token = os.environ[SLACK_SDK_TEST_BOT_TOKEN]
        self.sync_client: WebClient = WebClient(token=self.bot_token)
        self.async_client: AsyncWebClient = AsyncWebClient(token=self.bot_token)
        self.channel_id = os.environ[SLACK_SDK_TEST_WEB_TEST_CHANNEL_ID]
        self.user_id = os.environ[SLACK_SDK_TEST_WEB_TEST_USER_ID]

    def tearDown(self):
        pass

    def test_issue_594(self):
        client, logger = self.sync_client, self.logger
        external_url = "https://www.example.com/good-old-slack-logo"
        external_id = f"test-remote-file-{uuid4()}"
        current_dir = os.path.dirname(__file__)
        image = f"{current_dir}/../../tests/data/slack_logo.png"
        creation = client.files_remote_add(
            external_id=external_id,
            external_url=external_url,
            title="Good Old Slack Logo",
            indexable_file_contents="Good Old Slack Logo".encode("utf-8"),
            preview_image=image,
        )
        self.assertIsNotNone(creation)

        sharing = client.files_remote_share(channels=self.channel_id, external_id=external_id)
        self.assertIsNotNone(sharing)

        message = client.chat_postEphemeral(
            channel=self.channel_id,
            user=self.user_id,
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "This is a mrkdwn section block :ghost: *this is bold*, and ~this is crossed out~, and <https://google.com|this is a link>",
                    },
                },
                {
                    "type": "file",
                    "external_id": external_id,
                    "source": "remote",
                },
            ],
        )
        self.assertIsNotNone(message)

    def test_no_preview_image(self):
        client, logger = self.sync_client, self.logger
        external_url = "https://www.example.com/what-is-slack"
        external_id = f"test-remote-file-{uuid4()}"
        creation = client.files_remote_add(
            external_id=external_id,
            external_url=external_url,
            title="Slack (Wikipedia)",
            indexable_file_contents="Slack is a proprietary business communication platform developed by Slack Technologies.".encode(
                "utf-8"
            ),
        )
        self.assertIsNotNone(creation)

        sharing = client.files_remote_share(channels=self.channel_id, external_id=external_id)
        self.assertIsNotNone(sharing)

        message = client.chat_postEphemeral(
            channel=self.channel_id,
            user=self.user_id,
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "This is a mrkdwn section block :ghost: *this is bold*, and ~this is crossed out~, and <https://google.com|this is a link>",
                    },
                },
                {
                    "type": "file",
                    "external_id": external_id,
                    "source": "remote",
                },
            ],
        )
        self.assertIsNotNone(message)
