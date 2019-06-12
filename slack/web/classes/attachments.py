from typing import Iterable, List, Set

from .actions import Action
from .blocks import Block
from .objects import JsonObject, JsonValidator, extract_json


class Field(JsonObject):
    attributes = {"short", "value", "title"}

    def __init__(self, *, title: str = None, value: str = None, short: bool = True):
        self.title = title
        self.value = value
        self.short = short


class Author(JsonObject):
    attributes = {"author_name", "author_icon", "author_link"}

    def __init__(
        self, *, author_name: str, author_link: str = None, author_icon: str = None
    ):
        self.author_name = author_name
        self.author_link = author_link
        self.author_icon = author_icon

    @JsonValidator("author_name must be present if author_link is present")
    def author_link_without_author_name(self):
        return self.author_link is None or self.author_name is not None

    @JsonValidator("author_icon must be present if author_link is present")
    def author_link_without_author_icon(self):
        return self.author_link is None or self.author_icon is not None


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
        *,
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

    @JsonValidator("footer attribute cannot exceed 300 characters")
    def footer_length(self):
        return self.footer is None or len(self.footer) <= 300

    @JsonValidator("ts attribute cannot be present if footer attribute is absent")
    def ts_without_footer(self):
        return self.ts is None or self.footer is not None

    def get_json(self) -> dict:
        json = super().get_json()
        json.update(
            {"mrkdwn_in": ["fields"], "fields": extract_json(self.fields, Field)}
        )
        return json


class BlockAttachment(Attachment):
    """
    Attachment created directly from blocks
    """

    blocks: List[Block]

    def __init__(self, *, blocks: Iterable[Block]):
        super().__init__(text="")
        self.blocks = list(blocks)

    def get_json(self) -> dict:
        return {"blocks": extract_json(self.blocks, Block)}


class InteractiveAttachment(Attachment):
    """
    An attachment built to allow interactive message handling/callbacks
    """

    actions: List[Action]

    @property
    def attributes(self) -> Set[str]:
        return super().attributes.union({"callback_id"})

    def __init__(
        self, *, callback_id: str, actions: Iterable[Action] = None, text="", **kwargs
    ):
        super().__init__(text=text, **kwargs)
        self.callback_id = callback_id
        self.actions = actions or []

    def get_json(self) -> dict:
        json = super().get_json()
        json["actions"] = extract_json(self.actions, Action)
        return json
