import unittest

from slack_sdk.models.metadata import (
    EventAndEntityMetadata,
    EntityMetadata,
    ExternalRef,
    EntityPayload,
    EntityAttributes,
    EntityTitle,
    TaskEntityFields,
    EntityStringField,
    EntityTitle,
    EntityAttributes,
    TaskEntityFields,
    EntityTypedField,
    EntityStringField,
    EntityTimestampField,
    EntityEditSupport,
    EntityEditTextConfig,
    EntityCustomField,
    EntityUserIDField,
    EntityUserField,
    EntityIconField
)


class EntityMetadataTests(unittest.TestCase):
    maxDiff = None
    def test_creation(self):
        fields = TaskEntityFields(
            date_created=EntityTimestampField(value=1741164235),
            status=EntityStringField(value="In Progress"),
            description=EntityStringField(
                value="My Description",
                long=True,
                edit=EntityEditSupport(enabled=True, text=EntityEditTextConfig(min_length=5, max_length=100)),
            ),
            due_date=EntityTypedField(value="2026-06-06", type="slack#/types/date"),
            created_by=EntityTypedField(
                type="slack#/types/user",
                user=EntityUserIDField(user_id="USLACKBOT"),
            )
        )                     
        custom_fields = [
            EntityCustomField(
                label="My Users",
                key="my-users",
                type="array",
                item_type="slack#/types/user",
                value=[
                        EntityTypedField(
                            type="slack#/types/user",
                            user=EntityUserIDField(user_id="USLACKBOT")
                        ),
                        EntityTypedField(
                            type="slack#/types/user",
                            user=EntityUserField(
                                text="John Smith",
                                email="j@example.com",
                                icon=EntityIconField(alt_text="Avatar", url="https://my-hosted-icon.com")
                            ),
                        ),
                    ]
            )
        ]
        entity_metadata = EventAndEntityMetadata(
            entities=[
                EntityMetadata(
                    entity_type="slack#/entities/task",
                    external_ref=ExternalRef(id="123"),
                    url="https://myappdomain.com/123",
                    app_unfurl_url="https://myappdomain.com/123?myquery=param",
                    entity_payload=EntityPayload(
                        attributes=EntityAttributes(title=EntityTitle(text="My Title"), product_name="My Product", display_type="Incident", display_id="123"), 
                        fields=fields,
                        custom_fields=custom_fields,
                        display_order=["status", "due_date", "description"]
                    )
                )
            ]
        )
        
        self.assertDictEqual(
            entity_metadata.to_dict(),
            {
                "entities": [
                {
                    "app_unfurl_url": "https://myappdomain.com/123?myquery=param",
                    "entity_type": "slack#/entities/task",
                    "url": "https://myappdomain.com/123",
                    "external_ref": {
                    "id": "123"
                    },
                    "entity_payload": {
                        "attributes": {
                            "title": {
                                "text": "My Title"
                            },
                            "display_type": "Incident",
                            "display_id": "123",
                            "product_name": "My Product"
                        },
                        "fields": {
                            "date_created": {
                                "value": 1741164235
                            },
                            "status": {
                                "value": "In Progress"
                            },
                            "description": {
                                "value": "My Description",
                                "long": True,
                                "edit": {
                                    "enabled": True,
                                    "text": {
                                        "min_length": 5,
                                        "max_length": 100
                                    }
                                }
                            },
                            "due_date": {
                                "value": "2026-06-06",
                                "type": "slack#/types/date"
                            },
                            "created_by": {
                                "type": "slack#/types/user",
                                "user": {
                                    "user_id": "USLACKBOT"
                                }
                            }
                        },
                        "custom_fields": [
                            {
                                "label": "My Users",
                                "key": "my-users",
                                "type": "array",
                                "item_type": "slack#/types/user",
                                "value": [
                                    {
                                        "type": "slack#/types/user",
                                        "user": {
                                            "user_id": "USLACKBOT"
                                        }
                                    },
                                    {
                                        "type": "slack#/types/user",
                                        "user": {
                                            "text": "John Smith",
                                            "email": "j@example.com",
                                            "icon": {
                                            "alt_text": "Avatar",
                                            "url": "https://my-hosted-icon.com"
                                            }
                                        }
                                    }
                                ]
                            }
                        ],
                        "display_order": [
                            "status",
                            "due_date",
                            "description"
                        ]
                        }
                }]
            }
        )
