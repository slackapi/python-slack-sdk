from typing import Iterable, List

from .actions import Action
from .blocks import Block
from .objects import JsonObject
from ...errors import SlackObjectFormationError


class Field(JsonObject):
    attributes = {"short", "value", "title"}

    def __init__(self, title: str = None, value: str = None, short: bool = True):
        self.title = title
        self.value = value
        self.short = short

    def get_json(self) -> dict:
        return self.get_non_null_keys(self.attributes)


class Author(JsonObject):
    attributes = {"author_name", "author_icon", "author_link"}

    def __init__(
        self, author_name: str, author_link: str = None, author_icon: str = None
    ):
        self.author_name = author_name
        self.author_link = author_link
        self.author_icon = author_icon

    def get_json(self) -> dict:
        if not (self.author_link is None or self.author_name is not None):
            raise SlackObjectFormationError(
                "Author name is required if author link is populated"
            )
        if not (self.author_icon is None or self.author_name is not None):
            raise SlackObjectFormationError(
                "Author name is required if author icon is populated"
            )
        return self.get_non_null_keys(self.attributes)


class Attachment(JsonObject):
    attributes = {
        "title",
        "author",
        "pretext",
        "color",
        "text",
        "ts",
        "fallback",
        "footer",
        "thumb_url",
        "footer_icon",
        "fields",
        "title_link",
        "image_url",
    }

    author: Author
    fields: List[Field]
    actions: List[Action]

    def __init__(
        self,
        text: str,
        title: str = None,
        fallback: str = None,
        pretext: str = None,
        title_link: str = None,
        fields: Iterable[Field] = None,
        color: str = None,
        author: Author = None,
        image_url: str = None,
        thumb_url: str = None,
        footer: str = None,
        footer_icon: str = None,
        ts: int = None,
    ):
        self.text = text
        self.title = title
        self.fallback = fallback
        self.pretext = pretext
        self.title_link = title_link
        self.color = color
        self.author = author
        self.image_url = image_url
        self.thumb_url = thumb_url
        self.footer = footer
        self.footer_icon = footer_icon
        self.ts = ts
        self.fields = fields or []

    def get_json(self) -> dict:
        if self.footer is not None and len(self.footer) <= 300:
            raise SlackObjectFormationError(
                "Footer length cannot exceed 300 characters"
            )
        if self.ts is not None and self.footer is None:
            raise SlackObjectFormationError(
                "ts attribute cannot be specified if footer is not specified"
            )
        json = self.get_non_null_keys(self.attributes)
        json.update(
            {
                "mrkdwn_in": ["fields"],
                "fields": [field.get_json() for field in self.fields],
            }
        )
        return json


class BlockAttachment(Attachment):
    """
    Attachment created directly from blocks
    """

    blocks: List[Block]

    def __init__(self, blocks: Iterable[Block]):
        super().__init__(text="")
        self.blocks = list(blocks)

    def get_json(self) -> dict:
        return {"blocks": [block.get_json() for block in self.blocks]}


class InteractiveAttachment(Attachment):
    """
    An attachment built to allow interactive message handling/callbacks
    """

    actions: List[Action]

    def __init__(
        self, callback_id: str, actions: Iterable[Action] = None, text="", **kwargs
    ):
        super().__init__(text=text, **kwargs)
        self.callback_id = callback_id
        self.actions = actions or []

    def get_json(self) -> dict:
        json = super().get_json()
        json["callback_id"] = self.callback_id
        json["actions"] = [action.get_json() for action in self.actions]
        return json
