import logging
import os
import time
import unittest

from integration_tests.env_variable_names import SLACK_SDK_TEST_BOT_TOKEN
from slack_sdk.models.metadata import Metadata
from slack_sdk.web import WebClient


class TestWebClient(unittest.TestCase):
    def setUp(self):
        self.logger = logging.getLogger(__name__)
        self.bot_token = os.environ[SLACK_SDK_TEST_BOT_TOKEN]

    def tearDown(self):
        pass

    def test_publishing_message_metadata(self):
        client: WebClient = WebClient(token=self.bot_token)
        new_message = client.chat_postMessage(
            channel="#random",
            text="message with metadata",
            metadata={
                "event_type": "procurement-task",
                "event_payload": {
                    "id": "11111",
                    "amount": 5000,
                    "tags": ["foo", "bar", "baz"],
                },
            },
        )
        self.assertIsNone(new_message.get("error"))
        self.assertIsNotNone(new_message.get("message").get("metadata"))

        history = client.conversations_history(
            channel=new_message.get("channel"),
            limit=1,
            include_all_metadata=True,
        )
        self.assertIsNone(history.get("error"))
        self.assertIsNotNone(history.get("messages")[0].get("metadata"))

        modification = client.chat_update(
            channel=new_message.get("channel"),
            ts=new_message.get("ts"),
            text="message with metadata (modified)",
            metadata={
                "event_type": "procurement-task",
                "event_payload": {
                    "id": "11111",
                    "amount": 6000,
                },
            },
        )
        self.assertIsNone(modification.get("error"))
        self.assertIsNotNone(modification.get("message").get("metadata"))

        scheduled = client.chat_scheduleMessage(
            channel=new_message.get("channel"),
            post_at=int(time.time()) + 30,
            text="message with metadata (scheduled)",
            metadata={
                "event_type": "procurement-task",
                "event_payload": {
                    "id": "11111",
                    "amount": 10,
                },
            },
        )
        self.assertIsNone(scheduled.get("error"))
        self.assertIsNotNone(scheduled.get("message").get("metadata"))

    def test_publishing_message_metadata_using_models(self):
        client: WebClient = WebClient(token=self.bot_token)
        new_message = client.chat_postMessage(
            channel="#random",
            text="message with metadata",
            metadata=Metadata(
                event_type="procurement-task",
                event_payload={
                    "id": "11111",
                    "amount": 5000,
                    "tags": ["foo", "bar", "baz"],
                },
            ),
        )
        self.assertIsNone(new_message.get("error"))
        self.assertIsNotNone(new_message.get("message").get("metadata"))

        history = client.conversations_history(
            channel=new_message.get("channel"),
            limit=1,
            include_all_metadata=True,
        )
        self.assertIsNone(history.get("error"))
        self.assertIsNotNone(history.get("messages")[0].get("metadata"))

        modification = client.chat_update(
            channel=new_message.get("channel"),
            ts=new_message.get("ts"),
            text="message with metadata (modified)",
            metadata=Metadata(
                event_type="procurement-task",
                event_payload={
                    "id": "11111",
                    "amount": 6000,
                },
            ),
        )
        self.assertIsNone(modification.get("error"))
        self.assertIsNotNone(modification.get("message").get("metadata"))

        scheduled = client.chat_scheduleMessage(
            channel=new_message.get("channel"),
            post_at=int(time.time()) + 30,
            text="message with metadata (scheduled)",
            metadata=Metadata(
                event_type="procurement-task",
                event_payload={
                    "id": "11111",
                    "amount": 10,
                },
            ),
        )
        self.assertIsNone(scheduled.get("error"))
        self.assertIsNotNone(scheduled.get("message").get("metadata"))
