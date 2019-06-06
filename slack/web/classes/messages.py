from typing import Iterable

from .attachments import Attachment
from .blocks import Block, SectionBlock
from .objects import JsonObject


class Message(JsonObject):
    """
    A general purpose message object.
    """

    API_CALL = "chat.postMessage"

    def __init__(self, text: str, target: str, thread_ts: str = None):
        assert target is not None

        self.channel = target
        self.text = text
        self.thread_ts = thread_ts
        self.attachments = []
        self.blocks = []

    def get_json(self):
        if self.text and self.blocks:
            #  Slack doesn't render the text property if there are blocks, so:
            self.blocks.insert(0, SectionBlock(self.text))
        json = {
            "text": self.text,
            "channel": self.channel,
            "attachments": [
                a.get_json() if isinstance(a, JsonObject) else a
                for a in self.attachments
            ],
            "blocks": [
                b.get_json() if isinstance(b, JsonObject) else b for b in self.blocks
            ],
            "as_user": True,
        }
        if self.thread_ts is not None:
            json["thread_ts"] = self.thread_ts
        return json


class Reply(Message):
    """
    Convenience class for creating a new response message directly from an incoming
    message event
    """

    def __init__(self, text: str, source_event: dict):
        channel = source_event["channel"]
        thread_ts = source_event.get("thread_ts")
        super().__init__(text, target=channel, thread_ts=thread_ts)


class EphemeralMessage(Message):
    """
    Ephemeral messages are only visible to the target user, and disappear when they
    close their session/client
    """

    API_CALL = "chat.postEphemeral"

    def __init__(self, text: str, target_user: str, channel: str):
        super().__init__(text, target=channel)
        self.target_user = target_user

    def get_json(self):
        json = super().get_json()
        json["user"] = self.target_user
        return json


class MessageUpdate(JsonObject):
    """
    Update an existing message (specified by channel and ts) with new text and/or
    attachments
    """

    required_attributes = {"channel", "ts"}
    optional_attributes = {"text", "attachments", "blocks"}

    def __init__(
        self,
        channel: str,
        ts: str,
        text: str = None,
        attachments: Iterable[Attachment] = None,
        blocks: Iterable[Block] = None,
    ):

        self.channel = channel
        self.ts = ts
        self.text = text
        self.attachments = attachments
        self.blocks = blocks

    def get_json(self):
        json = self.get_non_null_keys(self.required_attributes)
        updates = self.get_non_null_keys(self.optional_attributes)
        if updates.get("text"):
            json["text"] = updates["text"]
        if updates.get("attachments"):
            json["attachments"] = [
                a.get_json() if isinstance(a, JsonObject) else a
                for a in updates["attachments"]
            ]
        if updates.get("blocks"):
            json["blocks"] = [
                b.get_json() if isinstance(b, JsonObject) else b
                for b in updates["blocks"]
            ]
        return json
