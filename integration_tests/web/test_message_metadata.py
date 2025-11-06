import logging
import os
import time
import unittest
import json

from integration_tests.env_variable_names import SLACK_SDK_TEST_BOT_TOKEN
from slack_sdk.models.metadata import (
    Metadata, EventAndEntityMetadata, EntityMetadata, EntityType, ExternalRef, 
    EntityPayload, EntityAttributes, EntityTitle, TaskEntityFields, EntityStringField,
    EntityTitle, EntityAttributes, EntityFullSizePreview,
    TaskEntityFields, EntityTypedField, EntityStringField, EntityTimestampField,
    EntityEditSupport, EntityEditTextConfig, EntityCustomField, EntityUserIDField,
    EntityIconField, ExternalRef as CustomExternalRef
)
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

    def test_publishing_entity_metadata(self):
        client: WebClient = WebClient(token=self.bot_token,base_url='https://dev.slack.com/api/')
        new_message = client.chat_postMessage(
            channel="C014KLZN9M0",
            text="Message with entity metadata",
            metadata={"entities": [{
                "entity_type": "slack#/entities/task",
                "url": "https://abc.com/123",
                "external_ref": {"id": "123"},
                "entity_payload": {
                    "attributes": {
                        "title": {"text": "My task"},
                        "product_name": "We reference only"
                    },
                    "fields": {
                        "due_date": {
                            "value": "2026-06-06",
                            "type": "slack#/types/date",
                            "edit": {"enabled": True}
                        },
                        "created_by": {
                            "type": "slack#/types/user",
                            "user": {"user_id": "U014KLZE350"}
                        },
                        "date_created": {"value": 1760629278}
                    },
                    "custom_fields": [
                        {
                        "label": "img",
                        "key": "img",
                        "type": "slack#/types/image",
                        "image_url": "https://s3-media2.fl.yelpcdn.com/bphoto/korel-1YjNtFtJlMTaC26A/o.jpg"
                        }
                    ]
                }
            }]}
        )
 
        self.assertIsNone(new_message.get("error"))
        self.assertIsNone(new_message.get("warning"))

    def test_publishing_entity_metadata_using_models(self):
        
        # Build the metadata
        
        title = EntityTitle(text="My title")
        full_size_preview = EntityFullSizePreview(
            is_supported=True,
            preview_url="https://s3-media3.fl.yelpcdn.com/bphoto/c7ed05m9lC2EmA3Aruue7A/o.jpg",
            mime_type="image/jpeg"
        )
        attributes = EntityAttributes(
            title=title,
            product_name="My Product",
            full_size_preview=full_size_preview
        )
        description = EntityStringField(
            value="Description of the task.",
            long=True,
            edit=EntityEditSupport(
                enabled=True,
                text=EntityEditTextConfig(
                    min_length=5,
                    max_length=100
                )
            )
        )
        due_date = EntityTypedField(
            value="2026-06-06",
            type="slack#/types/date",
            edit=EntityEditSupport(enabled=True)
        )
        created_by = EntityTypedField(
            type="slack#/types/user",
            user=EntityUserIDField(user_id="USLACKBOT"),
        )
        date_created = EntityTimestampField(
            value=1762450663,
            type="slack#/types/timestamp"
        )
        date_updated = EntityTimestampField(
            value=1762450663,
            type="slack#/types/timestamp"
        )
        fields = TaskEntityFields(
            description=description,
            due_date=due_date,
            created_by=created_by,
            date_created=date_created,
            date_updated=date_updated
        )
        custom_fields = []
        custom_fields.append(EntityCustomField(
            label="My Image",
            key="my-image",
            type="slack#/types/image",
            image_url="https://s3-media3.fl.yelpcdn.com/bphoto/c7ed05m9lC2EmA3Aruue7A/o.jpg"
        ))
        entity = EntityPayload(
            attributes=attributes,
            fields=fields,
            custom_fields=custom_fields
        )

        client: WebClient = WebClient(token=self.bot_token,base_url='https://dev.slack.com/api/')
        new_message = client.chat_postMessage(
            channel="C014KLZN9M0",
            text="Message with entity metadata",
            metadata=EventAndEntityMetadata(
                entities=[
                    EntityMetadata(
                    entity_type=EntityType.TASK,
                    external_ref=ExternalRef(id="abc123"),
                    url="https://myappdomain.com",
                    entity_payload=entity,
            )]),
        )
 
        self.assertIsNone(new_message.get("error"))
        self.assertIsNone(new_message.get("warning"))
