from typing import List

from .attachments import Attachment
from .blocks import Block, SectionBlock
from .objects import JsonObject


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

    def get_json(self):
        if self.text and self.blocks:
            #  Slack doesn't render the text property if there are blocks, so:
            self.blocks.insert(0, SectionBlock(text=self.text))
        json = {
            "text": self.text,
            "attachments": [
                a.get_json() if isinstance(a, Attachment) else a
                for a in self.attachments
            ],
            "blocks": [
                b.get_json() if isinstance(b, Block) else b for b in self.blocks
            ],
        }
        return json
