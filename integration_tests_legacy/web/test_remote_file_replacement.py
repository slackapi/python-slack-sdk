import os
import time
import unittest
from uuid import uuid4

from integration_tests.env_variable_names import \
    SLACK_SDK_TEST_BOT_TOKEN, \
    SLACK_SDK_TEST_WEB_TEST_CHANNEL_ID
from slack import WebClient


class TestWebClient(unittest.TestCase):
    """
    Suggestion for https://github.com/slackapi/python-slackclient/issues/762
    """

    def setUp(self):
        self.bot_token = os.environ[SLACK_SDK_TEST_BOT_TOKEN]
        self.channel_id = os.environ[SLACK_SDK_TEST_WEB_TEST_CHANNEL_ID]

    def tearDown(self):
        pass

    def test_replacing_remote_file_blocks_in_a_message(self):
        client: WebClient = WebClient(token=self.bot_token, run_async=False)
        current_dir = os.path.dirname(__file__)
        url = "https://www.example.com/slack-logo"

        external_id = f"remote-file-slack-logo-{uuid4()}"
        remote_file_creation = client.files_remote_add(
            external_id=external_id,
            external_url=url,
            title="Slack Logo",
            preview_image=f"{current_dir}/../../tests/data/slack_logo.png"
        )
        self.assertIsNotNone(remote_file_creation)

        new_message = client.chat_postMessage(
            channel=self.channel_id,
            text="Slack Logo v1",
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "plain_text",
                        "text": "This is v1"
                    }
                },
                {
                    "type": "file",
                    "external_id": external_id,
                    "source": "remote",
                }
            ],
        )
        self.assertIsNotNone(new_message)
        message_ts = new_message["message"]["ts"]

        time.sleep(2)

        external_id = f"remote-file-slack-logo-{uuid4()}"
        new_version = client.files_remote_add(
            external_id=external_id,
            external_url=url,
            title="Slack Logo",
            preview_image=f"{current_dir}/../../tests/data/slack_logo_new.png"
        )
        self.assertIsNotNone(new_version)

        time.sleep(3)

        modification = client.chat_update(
            channel=self.channel_id,
            ts=message_ts,
            text="Slack Logo v2",
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "plain_text",
                        "text": "This is v2"
                    }
                },
                {
                    "type": "file",
                    "external_id": external_id,
                    "source": "remote",
                }
            ],
        )
        self.assertIsNotNone(modification)
