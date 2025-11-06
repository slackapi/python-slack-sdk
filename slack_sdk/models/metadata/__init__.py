from typing import Dict, Any, Union
from enum import StrEnum
from slack_sdk.models.basic_objects import JsonObject


class Metadata(JsonObject):
    """Message metadata

    https://docs.slack.dev/messaging/message-metadata/
    """

    attributes = {
        "event_type",
        "event_payload",
    }

    def __init__(
        self,
        event_type: str,
        event_payload: Dict[str, Any],
        **kwargs,
    ):
        self.event_type = event_type
        self.event_payload = event_payload
        self.additional_attributes = kwargs

    def __str__(self):
        return str(self.get_non_null_attributes())

    def __repr__(self):
        return self.__str__()


## Work object entity metadata

class EntityType(StrEnum):
    FILE = "slack#/entities/file"
    TASK = "slack#/entities/task"
    ITEM = "slack#/entities/item"
    INCIDENT = "slack#/entities/incident"
    CONTENT_ITEM = "slack#/entities/content_item"


class ExternalRef(JsonObject):
    attributes = {
        "id",
        "type",
    }
    def __init__(
        self,
        id: str,
        type: str = None,
        **kwargs,
    ):
        self.id = id
        self.type = type
        self.additional_attributes = kwargs

    def __str__(self):
        return str(self.get_non_null_attributes())

    def __repr__(self):
        return self.__str__()

class Title(JsonObject):
    attributes = {
        "text",
        "edit",
    }
    def __init__(
        self,
        text: str,
        edit: Dict[str, Any] = None, # TODO EntityEditSupport
        **kwargs,
    ):
        self.text = text
        self.edit = edit
        self.additional_attributes = kwargs

    def __str__(self):
        return str(self.get_non_null_attributes())

    def __repr__(self):
        return self.__str__()


class Attributes(JsonObject):
    attributes = {
        "title",
        "display_type",
        "display_id",
        "product_icon"
        "product_name"
        "locale"
        "full_size_preview"
        "metadata_last_modified"
    }
    def __init__(
        self,
        title: Title,
        display_type: str = None,
        display_id: str = None,
        product_icon: Dict[str, Any] = None,
        product_name: str = None,
        locale: str = None,
        full_size_preview: str = None,
        metadata_last_modified: int = None,
        **kwargs,
    ):
        self.title = title
        self.display_type = display_type
        self.display_id = display_id
        self.product_icon = product_icon
        self.product_name = product_name
        self.locale = locale
        self.full_size_preview = full_size_preview
        self.metadata_last_modified = metadata_last_modified
        self.additional_attributes = kwargs

    def __str__(self):
        return str(self.get_non_null_attributes())

    def __repr__(self):
        return self.__str__()


class EntityPayload(JsonObject):
    attributes = {
        "attributes"
    }
    def __init__(
        self,
        attributes: Attributes,
        **kwargs,
    ):
        self.attributes = attributes
        # TODO
        self.additional_attributes = kwargs

    def __str__(self):
        return str(self.get_non_null_attributes())

    def __repr__(self):
        return self.__str__()


class EntityMetadata(JsonObject):
    """Work object entity metadata

    https://docs.slack.dev/messaging/work-objects/
    """

    attributes = {
        "entity_type",
        "external_ref",
        "url",
        "app_unfurl_url",
        "entity_payload",
    }

    def __init__(
        self,
        entity_type: Union[str, EntityType],
        external_ref: Union[Dict[str, Any], ExternalRef],
        url: str,
        entity_payload: Union[Dict[str, Any], EntityPayload],
        app_unfurl_url: str = None,
        **kwargs,
    ):
        self.entity_type = entity_type
        self.external_ref = external_ref
        self.url = url
        self.app_unfurl_url = app_unfurl_url
        self.entity_payload = entity_payload
        self.additional_attributes = kwargs

    def __str__(self):
        return str(self.get_non_null_attributes())

    def __repr__(self):
        return self.__str__()


class EventAndEntityMetadata(JsonObject):
    """Message metadata

    https://docs.slack.dev/messaging/message-metadata/
    """

    attributes = {"event_type", "event_payload", "entities"}

    def __init__(
        self,
        event_type: str = None,
        event_payload: Dict[str, Any] = None,
        entities: list[EntityMetadata] = None,
        **kwargs,
    ):
        self.event_type = event_type
        self.event_payload = event_payload
        self.entities = entities
        self.additional_attributes = kwargs

    def __str__(self):
        return str(self.get_non_null_attributes())

    def __repr__(self):
        return self.__str__()
