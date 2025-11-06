import logging
import os
import time
import unittest

from integration_tests.env_variable_names import SLACK_SDK_TEST_BOT_TOKEN
from slack_sdk.models.metadata import Metadata, EventAndEntityMetadata, EntityMetadata, EntityType, ExternalRef
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

    def test_publishing_message_entity_metadata_using_models(self):
        
        payload = { "attributes": { "title": { "text": "Work References" }, "product_name": "We reference only", "metadata_last_modified": 1760999279, "full_size_preview": { "is_supported": True } }, "fields": { "due_date": { "value": "2026-06-06", "type": "slack#/types/date", "edit": { "enabled": True } }, "created_by": { "type": "slack#/types/user", "user": { "user_id": "U014KLZE350" }, "edit": { "enabled": True } }, "description": { "value": "Initial task work object for test test test", "format": "markdown", "long": True, "edit": { "enabled": True, "text": { "min_length": 1, "max_length": 100 } } }, "date_created": { "value": 1760629278 }, "date_updated": { "value": 1760999279 } }, "custom_fields": [ { "label": "img", "key": "img", "type": "slack#/types/image", "image_url": "https://cdn.shopify.com/s/files/1/0156/3796/files/shutterstock_54266797_large.jpg?v=1549042211" }, { "label": "Reference tasks", "key": "ref-tasks", "type": "slack#/types/entity_ref", "entity_ref": { "entity_url": "https://app-one-app-two-auth-dev.tinyspeck.com/admin/slack/workobject/129/change/", "external_ref": { "id": "129" }, "title": "Radiant task", "display_type": "tasks", "icon": { "alt_text": "img", "url": "https://avatars.slack-edge.com/2024-09-05/7707480927360_791cc0c5cdf5b6720b21_512.png" } } }, { "label": "All related references", "key": "related-refs", "type": "array", "item_type": "slack#/types/entity_ref", "value": [ { "entity_ref": { "entity_url": "https://app-one-app-two-auth-dev.tinyspeck.com/admin/slack/workobject/131/change/", "external_ref": { "id": "131" }, "title": "Work object planner", "icon": { "alt_text": "img", "url": "https://avatars.slack-edge.com/2024-09-05/7707480927360_791cc0c5cdf5b6720b21_512.png" } } }, { "entity_ref": { "entity_url": "https://app-one-app-two-auth-dev.tinyspeck.com/admin/slack/workobject/133/change/", "external_ref": { "id": "133" }, "title": "Test" } }, { "entity_ref": { "entity_url": "https://app-one-app-two-auth-dev.tinyspeck.com/admin/slack/workobject/142/change/", "external_ref": { "id": "142" }, "title": "Test" } } ] } ] }
        
        client: WebClient = WebClient(token=self.bot_token,base_url='https://dev2378.slack.com/api/')
        new_message = client.chat_postMessage(
            channel="C014KLZN9M0",
            text="dbl check message with metadata",
            metadata=EventAndEntityMetadata(
                entities=[
                    EntityMetadata(
                    entity_type=EntityType.TASK,
                    external_ref=ExternalRef(id="abc123"),
                    url="https://myappdomain.com",
                    entity_payload=payload,
            )]),
        )
 
        self.assertIsNone(new_message.get("error"))
        self.assertIsNone(new_message.get("warning"))
