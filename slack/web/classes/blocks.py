from typing import List, Optional, Set, Union

from . import JsonObject, JsonValidator, extract_json
from .elements import BlockElement, InteractiveElement, AbstractSelector
from .objects import MarkdownTextObject, PlainTextObject, TextObject


class Block(JsonObject):
    """Blocks are a series of components that can be combined
    to create visually rich and compellingly interactive messages.

    You can include up to 50 blocks in each message.

    The lists of fields and values below describe the JSON that apps can use to generate each block:
    Section
    Divider
    Image
    Actions
    Context
    Input
    File
    """

    attributes = {"block_id"}

    block_id_max_length = 255

    def __init__(self, *, subtype: str, block_id: Optional[str] = None):
        self.subtype = subtype
        # subtype is actually the "type" parameter, but was renamed due to name already being used in Python Builtins.
        self.block_id = block_id
        self.color = None

    @JsonValidator(f"block_id cannot exceed {block_id_max_length} characters")
    def block_id_length(self):
        return self.block_id is None or len(self.block_id) <= self.block_id_max_length

    def to_dict(self) -> dict:
        json = super().to_dict()
        json["type"] = self.subtype
        return json


class SectionBlock(Block):
    fields_max_length = 10

    def __init__(
        self,
        *,
        text: Union[str, TextObject] = None,
        block_id: Optional[str] = None,
        fields: List[str] = None,
        accessory: Optional[BlockElement] = None,
    ):
        """
        A section is one of the most flexible blocks available.
        It can be used as a simple text block, in combination with
        text fields, or side-by-side with any of the available block elements.

        https://api.slack.com/reference/block-kit/blocks#section

        Args:
            text: The text for the block, in the form of string or a text object.
                Maximum length for the text in this field is 3000 characters.
            block_id: A string acting as a unique identifier for a block.
                You can use this block_id when you receive an interaction
                payload to identify the source of the action. If not
                specified, one will be generated. Maximum length for this
                field is 255 characters. block_id should be unique for each
                message and each iteration of a message.
                If a message is updated, use a new block_id.
            fields: optional: a sequence of strings that will be rendered using
                MarkdownTextObjects. Any strings included with fields will be rendered
                in a compact format that allows for 2 columns of side-by-side text.
                Maximum number of items is 10.
                Maximum length for the text in each item is 2000 characters.
            accessory: an optional BlockElement to attach to this SectionBlock as
                secondary content
        """
        super().__init__(subtype="section", block_id=block_id)
        self.text = text
        self.fields = fields or []
        self.accessory = accessory

    @JsonValidator("text or fields attribute must be specified")
    def text_or_fields_populated(self):
        return self.text is not None or self.fields

    @JsonValidator(f"fields attribute cannot exceed {fields_max_length} items")
    def fields_length(self):
        return self.fields is None or len(self.fields) <= self.fields_max_length

    def to_dict(self) -> dict:
        json = super().to_dict()
        if self.text is not None:
            if isinstance(self.text, TextObject):
                json["text"] = self.text.to_dict()
            else:
                json["text"] = MarkdownTextObject.direct_from_string(self.text)
        if self.fields:
            json["fields"] = [
                MarkdownTextObject.direct_from_string(field) for field in self.fields
            ]
        if self.accessory is not None:
            json["accessory"] = extract_json(self.accessory)
        return json


class DividerBlock(Block):
    def __init__(self, *, block_id: Optional[str] = None):
        """A content divider, like an <hr>, to split up different blocks inside of a message.

        Args:
            block_id: A string acting as a unique identifier for a block.
                You can use this block_id when you receive an interaction
                payload to identify the source of the action. If not
                specified, one will be generated. Maximum length for this
                field is 255 characters. block_id should be unique for each
                message and each iteration of a message.
                If a message is updated, use a new block_id.

        https://api.slack.com/reference/block-kit/blocks#divider
        """
        super().__init__(subtype="divider", block_id=block_id)


class ImageBlock(Block):
    @property
    def attributes(self) -> Set[str]:
        return super().attributes.union({"alt_text", "image_url"})

    image_url_max_length = 3000
    alt_text_max_length = 2000
    title_max_length = 2000

    def __init__(
        self,
        *,
        image_url: str,
        alt_text: str,
        title: Optional[str] = None,
        block_id: Optional[str] = None,
    ):
        """
        A simple image block, designed to make those cat photos really pop.

        https://api.slack.com/reference/block-kit/blocks#image

        Args:
            image_url: Publicly hosted URL to be displayed. Cannot exceed 3000
                characters.
            alt_text: Plain text summary of image. Cannot exceed 2000 characters.
            title: A title to be displayed above the image. Cannot exceed 2000
                characters.
            block_id: ID to be used for this block - autogenerated if left blank.
                Cannot exceed 255 characters.
        """
        super().__init__(subtype="image", block_id=block_id)
        self.image_url = image_url
        self.alt_text = alt_text
        self.title = title

    @JsonValidator(
        f"image_url attribute cannot exceed {image_url_max_length} characters"
    )
    def image_url_length(self):
        return len(self.image_url) <= self.image_url_max_length

    @JsonValidator(f"alt_text attribute cannot exceed {alt_text_max_length} characters")
    def alt_text_length(self):
        return len(self.alt_text) <= self.alt_text_max_length

    @JsonValidator(f"title attribute cannot exceed {title_max_length} characters")
    def title_length(self):
        return self.title is None or len(self.title) <= self.title_max_length

    def to_dict(self) -> dict:
        json = super().to_dict()
        if self.title is not None:
            json["title"] = PlainTextObject.direct_from_string(self.title)
        return json


class ActionsBlock(Block):
    elements_max_length = 5

    def __init__(
        self, *, elements: List[InteractiveElement], block_id: Optional[str] = None
    ):
        """
        A block that is used to hold interactive elements.

        https://api.slack.com/reference/block-kit/blocks#actions

        Args:
            elements: Up to 5 InteractiveElement objects - buttons, date pickers, etc
            block_id: ID to be used for this block - autogenerated if left blank.
                Cannot exceed 255 characters.
        """
        super().__init__(subtype="actions", block_id=block_id)
        self.elements = elements

    @JsonValidator(f"elements attribute cannot exceed {elements_max_length} elements")
    def elements_length(self):
        return len(self.elements) <= self.elements_max_length

    def to_dict(self) -> dict:
        json = super().to_dict()
        json["elements"] = extract_json(self.elements)
        return json


class ContextBlock(Block):
    elements_max_length = 10

    def __init__(
        self,
        *,
        elements: List[Union[ImageBlock, TextObject]],
        block_id: Optional[str] = None,
    ):
        """
        Displays message context, which can include both images and text.

        https://api.slack.com/reference/block-kit/blocks#context

        Args:
            elements: Up to 10 ImageElements and TextObjects
            block_id: ID to be used for this block - autogenerated if left blank.
                Cannot exceed 255 characters.
        """
        super().__init__(subtype="context", block_id=block_id)
        self.elements = elements

    @JsonValidator(f"elements attribute cannot exceed {elements_max_length} elements")
    def elements_length(self):
        return len(self.elements) <= self.elements_max_length

    def to_dict(self) -> dict:
        json = super().to_dict()
        json["elements"] = extract_json(self.elements)
        return json


class InputBlock(Block):
    attributes = {"label", "hint", "optional"}
    label_max_length = 2000
    hint_max_length = 2000

    def __init__(
        self,
        *,
        label: str,
        element: Union[str, AbstractSelector],
        hint: Optional[str] = None,
        optional: Optional[bool] = False,
    ):
        """
        A block that collects information from users - it can hold a plain-text input element,
        a select menu element, a multi-select menu element, or a datepicker.

        Important Note: Input blocks are only available in modals.

        https://api.slack.com/reference/block-kit/blocks#input

        Args:
            label: A label that appears above an input element in the
                form of a text object that must have type of plain_text.
                Maximum length for the text in this field is 2000 characters.
            element: An plain-text input element, a select menu element,
                a multi-select menu element, or a datepicker.
            hint: An optional hint that appears below an input element in a lighter grey.
                Maximum length for the text in this field is 2000 characters.
            optional: A boolean that indicates whether the input element
                may be empty when a user submits the modal. Defaults to false.
        """
        super().__init__(subtype="input")
        self.label = label
        self.element = element
        self.hint = hint
        self.optional = optional

    @JsonValidator(f"label attribute cannot exceed {label_max_length} characters")
    def label_length(self):
        return len(self.label) <= self.label_max_length

    @JsonValidator(f"hint attribute cannot exceed {hint_max_length} characters")
    def hint_length(self):
        return self.hint is None or len(self.hint) <= self.hint_max_length

    @JsonValidator(
        (
            "element attribute must be a string, select element, multi-select element, "
            "or a datepicker. (Subclasses of AbstractSelector)"
        )
    )
    def element_type(self):
        return isinstance(self.element, (str, AbstractSelector))

    def to_dict(self) -> dict:
        json = super().to_dict()
        if isinstance(self.element, str):
            json["element"] = PlainTextObject.direct_from_string(self.element)
        else:
            json["element"] = extract_json(self.element)
        return json


class FileBlock(Block):
    @property
    def attributes(self) -> Set[str]:
        return super().attributes.union({"external_id", "source"})

    def __init__(
        self,
        *,
        external_id: str,
        source: str = "remote",
        block_id: Optional[str] = None,
    ):
        """Displays a remote file.

        https://api.slack.com/reference/block-kit/blocks#file
        """
        super().__init__(subtype="file", block_id=block_id)
        self.external_id = external_id
        self.source = source
