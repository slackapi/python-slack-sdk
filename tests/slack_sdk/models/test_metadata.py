import unittest

from slack_sdk.models.metadata import (
    EventAndEntityMetadata,
    EntityMetadata,
    ExternalRef,
    FileEntitySlackFile,
    EntityIconField,
    EntityEditTextConfig,
    EntityEditSupport,
    EntityFullSizePreviewError,
    EntityFullSizePreview,
    EntityUserIDField,
    EntityUserField,
    EntityTypedField,
    EntityStringField,
    EntityTimestampField,
    EntityImageField,
    EntityCustomField,
    FileEntityFields,
    TaskEntityFields,
    EntityActionButton,
    EntityTitle,
    EntityAttributes,
    EntityActions,
    EntityPayload,
)


class EntityMetadataTests(unittest.TestCase):
    maxDiff = None

    # ============================================================================
    # Entity JSON
    # ============================================================================

    task_entity_json = {
        "app_unfurl_url": "https://myappdomain.com/123?myquery=param",
        "entity_type": "slack#/entities/task",
        "url": "https://myappdomain.com/123",
        "external_ref": {"id": "123"},
        "entity_payload": {
            "attributes": {
                "title": {"text": "My Title"},
                "display_type": "Incident",
                "display_id": "123",
                "product_name": "My Product",
            },
            "fields": {
                "date_created": {"value": 1741164235},
                "status": {"value": "In Progress"},
                "description": {
                    "value": "My Description",
                    "long": True,
                    "edit": {"enabled": True, "text": {"min_length": 5, "max_length": 100}},
                },
                "due_date": {"value": "2026-06-06", "type": "slack#/types/date"},
                "created_by": {"type": "slack#/types/user", "user": {"user_id": "USLACKBOT"}},
            },
            "custom_fields": [
                {
                    "label": "My Users",
                    "key": "my-users",
                    "type": "array",
                    "item_type": "slack#/types/user",
                    "value": [
                        {"type": "slack#/types/user", "user": {"user_id": "USLACKBOT"}},
                        {
                            "type": "slack#/types/user",
                            "user": {
                                "text": "John Smith",
                                "email": "j@example.com",
                                "icon": {"alt_text": "Avatar", "url": "https://my-hosted-icon.com"},
                            },
                        },
                    ],
                }
            ]
        },
    }

    file_entity_json = {
          "app_unfurl_url": "https://myappdomain.com/file/456?view=preview",
          "entity_type": "slack#/entities/file",
          "url": "https://myappdomain.com/file/456",
          "external_ref": {
            "id": "456",
            "type": "DOC"
          },
          "entity_payload": {
            "attributes": {
              "title": {
                "text": "Q4 Product Roadmap"
              },
              "display_type": "PDF Document",
              "display_id": "DOC-456",
              "product_icon": {
                "alt_text": "Product Logo",
                "url": "https://myappdomain.com/icons/logo.png"
              },
              "product_name": "FileVault Pro",
              "locale": "en-US",
              "full_size_preview": {
                "is_supported": True,
                "preview_url": "https://myappdomain.com/previews/456/full.png",
                "mime_type": "image/png"
              }
            },
            "fields": {
              "preview": {
                "alt_text": "Document preview thumbnail",
                "label": "Preview",
                "image_url": "https://myappdomain.com/previews/456/thumb.png",
                "type": "slack#/types/image"
              },
              "date_created": {
                "value": 1709554321,
                "type": "slack#/types/timestamp"
              },
              "mime_type": {
                "value": "application/pdf"
              }
            },
            "slack_file": {
              "id": "F123ABC456",
              "type": "pdf"
            },
            "display_order": [
              "date_created",
              "mime_type",
              "preview"
            ],
            "actions": {
              "primary_actions": [
                {
                  "text": "Open",
                  "action_id": "open_file",
                  "value": "456",
                  "style": "primary",
                  "url": "https://myappdomain.com/file/456/view"
                }
              ],
              "overflow_actions": [
                {
                  "text": "Delete",
                  "action_id": "delete_file",
                  "value": "456",
                  "style": "danger"
                }
              ]
            }
          }
        }

    # ============================================================================
    # Methods returning re-usable metadata components
    # ============================================================================

    def attributes(self):
        return EntityAttributes(
            title=EntityTitle(text="My Title"),
            product_name="My Product",
            display_type="Incident",
            display_id="123",
        )
    
    def sample_file_attributes(self):
        return EntityAttributes(
            title=EntityTitle(text="Q4 Product Roadmap"),
            display_type="PDF Document",
            display_id="DOC-456",
            product_icon=EntityIconField(alt_text="Product Logo", url="https://myappdomain.com/icons/logo.png"),
            product_name="FileVault Pro",
            locale="en-US",
            full_size_preview=EntityFullSizePreview(is_supported=True, preview_url="https://myappdomain.com/previews/456/full.png", mime_type="image/png")
        )

    def user_array_custom_field(self):
        return EntityCustomField(
            label="My Users",
            key="my-users",
            type="array",
            item_type="slack#/types/user",
            value=[
                EntityTypedField(type="slack#/types/user", user=EntityUserIDField(user_id="USLACKBOT")),
                EntityTypedField(
                    type="slack#/types/user",
                    user=EntityUserField(
                        text="John Smith",
                        email="j@example.com",
                        icon=EntityIconField(alt_text="Avatar", url="https://my-hosted-icon.com"),
                    ),
                ),
            ],
        )

    def task_fields(self):
        return TaskEntityFields(
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
            ),
        )
    
    def file_fields(self):
        return FileEntityFields(
            preview=EntityImageField(type="slack#/types/image", alt_text="Document preview thumbnail", label="Preview", image_url="https://myappdomain.com/previews/456/thumb.png"),
            date_created=EntityTimestampField(value=1709554321, type="slack#/types/timestamp"),
            mime_type=EntityStringField(value="application/pdf")
        )

    def supported_full_size_preview(self):
        return EntityFullSizePreview(
            is_supported=True, preview_url="https://example.com/preview.jpg", mime_type="image/jpeg"
        )

    def sample_file_actions(self):
        return EntityActions(
            primary_actions=[EntityActionButton(text="Open", action_id="open_file", value="456", style="primary", url="https://myappdomain.com/file/456/view")],
            overflow_actions=[EntityActionButton(text="Delete", action_id="delete_file", value="456", style="danger")]
        )

    # ============================================================================
    # Tests
    # ============================================================================

    def test_entity_full_size_preview_error(self):
        error = EntityFullSizePreviewError(code="not_found", message="File not found")
        self.assertDictEqual(error.to_dict(), {"code": "not_found", "message": "File not found"})

    def test_entity_full_size_preview_with_error(self):
        preview = EntityFullSizePreview(
            is_supported=False, error=EntityFullSizePreviewError(code="invalid_format", message="File not found")
        )
        result = preview.to_dict()
        self.assertFalse(result["is_supported"])
        self.assertIn("error", result)

    def test_attributes(self):
        self.assertDictEqual(
            self.attributes().to_dict(),
            self.task_entity_json["entity_payload"]["attributes"],
        )

    def test_sample_file_attributes(self):
        self.assertDictEqual(
            self.sample_file_attributes().to_dict(),
            self.file_entity_json["entity_payload"]["attributes"],
        )

    def test_array_custom_field(self):
        self.assertDictEqual(
            self.user_array_custom_field().to_dict(),
            self.task_entity_json["entity_payload"]["custom_fields"][0],
        )

    def test_task_fields(self):
        self.assertDictEqual(
            self.task_fields().to_dict(),
            self.task_entity_json["entity_payload"]["fields"],
        )
    
    def test_file_fields(self):
        self.assertDictEqual(
            self.file_fields().to_dict(),
            self.file_entity_json["entity_payload"]["fields"],
        )

    def test_sample_file_actions(self):
        self.assertDictEqual(
            self.sample_file_actions().to_dict(),
            self.file_entity_json["entity_payload"]["actions"],
        )

    def test_complete_task_entity_metadata(self):
        entity_metadata = EventAndEntityMetadata(
            entities=[
                EntityMetadata(
                    entity_type="slack#/entities/task",
                    external_ref=ExternalRef(id="123"),
                    url="https://myappdomain.com/123",
                    app_unfurl_url="https://myappdomain.com/123?myquery=param",
                    entity_payload=EntityPayload(
                        attributes=self.attributes(),
                        fields=self.task_fields(),
                        custom_fields=[self.user_array_custom_field()],
                    ),
                )
            ]
        )
        self.assertDictEqual(entity_metadata.to_dict(), {"entities": [self.task_entity_json]})

    def test_complete_file_entity_metadata(self):
        entity_metadata = EventAndEntityMetadata(
            entities=[
                EntityMetadata(
                    entity_type="slack#/entities/file",
                    external_ref=ExternalRef(id="456", type="DOC"),
                    url="https://myappdomain.com/file/456",
                    app_unfurl_url="https://myappdomain.com/file/456?view=preview",
                    entity_payload=EntityPayload(
                        attributes=self.sample_file_attributes(),
                        fields=self.file_fields(),
                        slack_file=FileEntitySlackFile(id="F123ABC456", type="pdf"),
                        display_order=["date_created", "mime_type", "preview"],
                        actions=self.sample_file_actions()
                    ),
                )
            ]
        )
        self.assertDictEqual(entity_metadata.to_dict(), {"entities": [self.file_entity_json]})
