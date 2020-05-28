import os
import unittest

from integration_tests.env_variable_names import SLACK_SDK_TEST_INCOMING_WEBHOOK_URL, \
    SLACK_SDK_TEST_INCOMING_WEBHOOK_CHANNEL_NAME, \
    SLACK_SDK_TEST_BOT_TOKEN
from slack import WebClient
from slack import WebhookClient
from slack.web.classes.blocks import SectionBlock, DividerBlock, ActionsBlock
from slack.web.classes.elements import ButtonElement
from slack.web.classes.objects import MarkdownTextObject, PlainTextObject


class TestWebhook(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_webhook(self):
        url = os.environ[SLACK_SDK_TEST_INCOMING_WEBHOOK_URL]
        webhook = WebhookClient(url)
        response = webhook.send({"text": "Hello!"})
        self.assertEqual(200, response.status_code)
        self.assertEqual("ok", response.body)

        token = os.environ[SLACK_SDK_TEST_BOT_TOKEN]
        channel_name = os.environ[SLACK_SDK_TEST_INCOMING_WEBHOOK_CHANNEL_NAME].replace("#", "")
        client = WebClient(token=token)
        channel_id = None
        for resp in client.conversations_list(limit=10):
            for c in resp["channels"]:
                if c["name"] == channel_name:
                    channel_id = c["id"]
                    break
            if channel_id is not None:
                break

        history = client.conversations_history(channel=channel_id, limit=1)
        self.assertIsNotNone(history)
        actual_text = history["messages"][0]["text"]
        self.assertEqual("Hello!", actual_text)

    def test_with_block_kit_classes(self):
        url = os.environ[SLACK_SDK_TEST_INCOMING_WEBHOOK_URL]
        webhook = WebhookClient(url)
        response = webhook.send({
            "text": "fallback",
            "blocks": [
                SectionBlock(
                    block_id="sb-id",
                    text=MarkdownTextObject(text="This is a mrkdwn text section block."),
                    fields=[
                        PlainTextObject(text="*this is plain_text text*", emoji=True),
                        MarkdownTextObject(text="*this is mrkdwn text*"),
                        PlainTextObject(text="*this is plain_text text*", emoji=True),
                    ]
                ),
                DividerBlock(),
                ActionsBlock(
                    elements=[
                        ButtonElement(
                            text=PlainTextObject(text="Create New Task", emoji=True),
                            style="primary",
                            value="create_task",
                        ),
                        ButtonElement(
                            text=PlainTextObject(text="Create New Project", emoji=True),
                            value="create_project",
                        ),
                        ButtonElement(
                            text=PlainTextObject(text="Help", emoji=True),
                            value="help",
                        ),
                    ],
                ),
            ]
        })
        self.assertEqual(200, response.status_code)
        self.assertEqual("ok", response.body)
