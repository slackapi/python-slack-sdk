import logging
from typing import List

from .attachments import Attachment
from .blocks import Block
from .objects import JsonObject, JsonValidator, extract_json


class Message(JsonObject):
    def __init__(
        self,
        *,
        text: str,
        attachments: List[Attachment] = None,
        blocks: List[Block] = None,
        markdown: bool = True,
    ):
        """
        Create a message.

        https://api.slack.com/messaging/composing#message-structure

        :param text: Plain or Slack Markdown-like text to display in the message.

        :param attachments: A list of Attachment objects to display after the rest of
            the message's content. More than 20 is not recommended, but the actual limit
            is 100

        :param blocks: A list of Block objects to attach to this message. If
            specified, the 'text' property is ignored (more specifically, it's used as a
            fallback on clients that can't render blocks)

        :param markdown: Whether to parse markdown into formatting such as
            bold/italics, or leave text completely unmodified.
        """
        self.text = text
        self.attachments = attachments or []
        self.blocks = blocks or []
        self.markdown = markdown

    @JsonValidator("attachments attribute cannot exceed 100 items")
    def attachments_length(self):
        return self.attachments is None or len(self.attachments) <= 100

    def get_json(self):
        self.validate_json()
        if len(self.text) > 40000:
            logging.getLogger(__name__).error(
                "Messages over 40,000 characters are automatically truncated by Slack"
            )
        if self.text and self.blocks:
            #  Slack doesn't render the text property if there are blocks, so:
            logging.getLogger(__name__).info(
                "text attribute is treated as fallback text if blocks are attached to "
                "a message - insert text as a new SectionBlock for it to be displayed"
            )
        return {
            "text": self.text,
            "attachments": extract_json(self.attachments, Attachment),
            "blocks": extract_json(self.blocks, Block),
            "mrkdwn": self.markdown,
        }
