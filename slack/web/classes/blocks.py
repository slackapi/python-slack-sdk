from typing import List, Union

from .elements import BlockElement, InteractiveElements
from .objects import JsonObject, MarkdownTextObject, PlainTextObject, TextObject


class Block(JsonObject):
    """
    Top level block - should only be used for type-hinting
    """

    attributes = {"type", "block_id"}

    def __init__(self, type: str, block_id: str = None):
        assert block_id is None or len(block_id) <= 255
        self.type = type
        self.block_id = block_id
        self.color = None

    def get_json(self) -> dict:
        return self.get_non_null_keys(self.attributes)


class DividerBlock(Block):
    def __init__(self):
        super().__init__("divider")


class SectionBlock(Block):
    """
    A general purpose block capable of holding text, fields (displayed in a semi-tabular
     format) and one 'accessory' element
    """

    def __init__(
        self,
        text: Union[str, TextObject] = None,
        fields: List[str] = None,
        block_id: str = None,
        accessory: BlockElement = None,
    ):
        super().__init__(type="section", block_id=block_id)
        assert text is not None or fields is not None
        assert fields is None or len(fields) <= 10
        self.text = text
        self.fields = fields or []
        self.accessory = accessory

    def get_json(self) -> dict:
        json = super().get_json()
        if self.text is not None:
            if isinstance(self.text, TextObject):
                json["text"] = self.text.get_json()
            else:
                json["text"] = MarkdownTextObject(self.text).get_json()
        if self.fields:
            json["fields"] = [
                MarkdownTextObject(field).get_json() for field in self.fields
            ]
        if self.accessory is not None:
            json["accessory"] = self.accessory.get_json()
        return json


class ImageBlock(Block):
    """
    Message block that holds an image
    """

    def __init__(
        self,
        image_url: str,
        alt_text: str,
        title: PlainTextObject = None,
        block_id: str = None,
    ):
        super().__init__(type="image", block_id=block_id)
        assert len(image_url) <= 3000
        assert len(alt_text) <= 2000
        self.image_url = image_url
        self.alt_text = alt_text
        self.title = title

    def get_json(self) -> dict:
        json = super().get_json()
        json["image_url"] = self.image_url
        json["alt_text"] = self.alt_text
        if self.title is not None:
            json["title"] = self.title.get_json()
        return json


class ActionsBlock(Block):
    """
    Base interactive block, capable of holding multiple buttons, dropdowns, datepickers,
     etc
    """

    def __init__(self, elements: List[InteractiveElements], block_id: str = None):
        super().__init__(type="actions", block_id=block_id)
        assert 0 < len(elements) <= 5
        self.elements = elements

    def get_json(self) -> dict:
        json = super().get_json()
        json["elements"] = [element.get_json() for element in self.elements]
        return json


class ContextBlock(Block):
    """
    Generally suitable for use as a footer or similar additional detail
    """

    def __init__(
        self, elements: List[Union[ImageBlock, TextObject]], block_id: str = None
    ):
        super().__init__(type="context", block_id=block_id)
        assert len(elements) <= 10
        self.elements = elements

    def get_json(self) -> dict:
        json = super().get_json()
        json["elements"] = [element.get_json() for element in self.elements]
        return json
