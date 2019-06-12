import logging
from typing import List

from .attachments import Attachment
from .blocks import Block, SectionBlock
from .objects import JsonObject, JsonValidator, extract_json


class Message(JsonObject):
    """
    A general purpose message object.
    """

    def __init__(
        self,
        *,
        text: str,
        attachments: List[Attachment] = None,
        blocks: List[Block] = None,
    ):
        self.text = text
        self.attachments = attachments or []
        self.blocks = blocks or []

    @JsonValidator("attachments attribute cannot exceed 100 items")
    def attachments_length(self):
        return self.attachments is None or len(self.attachments) <= 100

    def get_json(self):
        if len(self.text) > 40000:
            logging.getLogger(__name__).error(
                "Messages over 40,000 characters are automatically truncated by Slack"
            )
        if self.text and self.blocks:
            #  Slack doesn't render the text property if there are blocks, so:
            logging.getLogger(__name__).info(
                "Moved text attribute into a new block so that it is rendered by Slack"
            )
            self.blocks.insert(0, SectionBlock(text=self.text))
        self.validate_json()
        return {
            "text": self.text,
            "attachments": extract_json(self.attachments, Attachment),
            "blocks": extract_json(self.blocks, Block),
        }
