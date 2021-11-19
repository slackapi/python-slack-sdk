import copy
import logging
import warnings
from typing import Dict, Sequence, Optional, Set, Union, Any, List

from slack_sdk.models import show_unknown_key_warning
from slack_sdk.models.basic_objects import (
    JsonObject,
    JsonValidator,
)
from .basic_components import MarkdownTextObject
from .basic_components import PlainTextObject
from .basic_components import TextObject
from .block_elements import BlockElement
from .block_elements import ImageElement
from .block_elements import InputInteractiveElement
from .block_elements import InteractiveElement


# -------------------------------------------------
# Base Classes
# -------------------------------------------------


class Block(JsonObject):
    """Blocks are a series of components that can be combined
    to create visually rich and compellingly interactive messages.
    https://api.slack.com/reference/block-kit/blocks
    """

    attributes = {"block_id", "type"}
    block_id_max_length = 255
    logger = logging.getLogger(__name__)

    def _subtype_warning(self):  # skipcq: PYL-R0201
        warnings.warn(
            "subtype is deprecated since slackclient 2.6.0, use type instead",
            DeprecationWarning,
        )

    @property
    def subtype(self) -> Optional[str]:
        return self.type

    def __init__(
        self,
        *,
        type: Optional[str] = None,  # skipcq: PYL-W0622
        subtype: Optional[str] = None,  # deprecated
        block_id: Optional[str] = None,
    ):
        if subtype:
            self._subtype_warning()
        self.type = type if type else subtype
        self.block_id = block_id
        self.color = None

    @JsonValidator(f"block_id cannot exceed {block_id_max_length} characters")
    def _validate_block_id_length(self):
        return self.block_id is None or len(self.block_id) <= self.block_id_max_length

    @classmethod
    def parse(cls, block: Union[dict, "Block"]) -> Optional["Block"]:
        if block is None:  # skipcq: PYL-R1705
            return None
        elif isinstance(block, Block):
            return block
        else:
            if "type" in block:
                type = block["type"]  # skipcq: PYL-W0622
                if type == SectionBlock.type:  # skipcq: PYL-R1705
                    return SectionBlock(**block)
                elif type == DividerBlock.type:
                    return DividerBlock(**block)
                elif type == ImageBlock.type:
                    return ImageBlock(**block)
                elif type == ActionsBlock.type:
                    return ActionsBlock(**block)
                elif type == ContextBlock.type:
                    return ContextBlock(**block)
                elif type == InputBlock.type:
                    return InputBlock(**block)
                elif type == FileBlock.type:
                    return FileBlock(**block)
                elif type == CallBlock.type:
                    return CallBlock(**block)
                elif type == HeaderBlock.type:
                    return HeaderBlock(**block)
                else:
                    cls.logger.warning(f"Unknown block detected and skipped ({block})")
                    return None
            else:
                cls.logger.warning(f"Unknown block detected and skipped ({block})")
                return None

    @classmethod
    def parse_all(
        cls, blocks: Optional[Sequence[Union[dict, "Block"]]]
    ) -> List["Block"]:
        return [cls.parse(b) for b in blocks or []]


# -------------------------------------------------
# Block Classes
# -------------------------------------------------


class SectionBlock(Block):
    type = "section"
    fields_max_length = 10
    text_max_length = 3000

    @property
    def attributes(self) -> Set[str]:
        return super().attributes.union({"text", "fields", "accessory"})

    def __init__(
        self,
        *,
        block_id: Optional[str] = None,
        text: Optional[Union[str, dict, TextObject]] = None,
        fields: Optional[Sequence[Union[str, dict, TextObject]]] = None,
        accessory: Optional[Union[dict, BlockElement]] = None,
        **others: dict,
    ):
        """A section is one of the most flexible blocks available.
        https://api.slack.com/reference/block-kit/blocks#section

        Args:
            block_id (required): A string acting as a unique identifier for a block.
                If not specified, one will be generated.
                You can use this block_id when you receive an interaction payload to identify the source of the action.
                Maximum length for this field is 255 characters.
                block_id should be unique for each message and each iteration of a message.
                If a message is updated, use a new block_id.
            text (preferred): The text for the block, in the form of a text object.
                Maximum length for the text in this field is 3000 characters.
                This field is not required if a valid array of fields objects is provided instead.
            fields (required if no text is provided): Required if no text is provided.
                An array of text objects. Any text objects included with fields will be rendered
                in a compact format that allows for 2 columns of side-by-side text.
                Maximum number of items is 10. Maximum length for the text in each item is 2000 characters.
            accessory: One of the available element objects.
        """
        super().__init__(type=self.type, block_id=block_id)
        show_unknown_key_warning(self, others)

        self.text = TextObject.parse(text)
        field_objects = []
        for f in fields or []:
            if isinstance(f, str):
                field_objects.append(MarkdownTextObject.from_str(f))
            elif isinstance(f, TextObject):
                field_objects.append(f)
            elif isinstance(f, dict) and "type" in f:
                d = copy.copy(f)
                t = d.pop("type")
                if t == MarkdownTextObject.type:
                    field_objects.append(MarkdownTextObject(**d))
                else:
                    field_objects.append(PlainTextObject(**d))
            else:
                self.logger.warning(f"Unsupported filed detected and skipped {f}")
        self.fields = field_objects
        self.accessory = BlockElement.parse(accessory)

    @JsonValidator("text or fields attribute must be specified")
    def _validate_text_or_fields_populated(self):
        return self.text is not None or self.fields

    @JsonValidator(f"fields attribute cannot exceed {fields_max_length} items")
    def _validate_fields_length(self):
        return self.fields is None or len(self.fields) <= self.fields_max_length

    @JsonValidator(f"text attribute cannot exceed {text_max_length} characters")
    def _validate_alt_text_length(self):
        return self.text is None or len(self.text.text) <= self.text_max_length


class DividerBlock(Block):
    type = "divider"

    def __init__(
        self,
        *,
        block_id: Optional[str] = None,
        **others: dict,
    ):
        """A content divider, like an <hr>, to split up different blocks inside of a message.
        https://api.slack.com/reference/block-kit/blocks#divider

        Args:
            block_id: A string acting as a unique identifier for a block. If not specified, one will be generated.
                You can use this block_id when you receive an interaction payload to identify the source of the action.
                Maximum length for this field is 255 characters.
                block_id should be unique for each message and each iteration of a message.
                If a message is updated, use a new block_id.
        """
        super().__init__(type=self.type, block_id=block_id)
        show_unknown_key_warning(self, others)


class ImageBlock(Block):
    type = "image"

    @property
    def attributes(self) -> Set[str]:
        return super().attributes.union({"alt_text", "image_url", "title"})

    image_url_max_length = 3000
    alt_text_max_length = 2000
    title_max_length = 2000

    def __init__(
        self,
        *,
        image_url: str,
        alt_text: str,
        title: Optional[Union[str, dict, TextObject]] = None,
        block_id: Optional[str] = None,
        **others: dict,
    ):
        """A simple image block, designed to make those cat photos really pop.
        https://api.slack.com/reference/block-kit/blocks#image

        Args:
            image_url (required): The URL of the image to be displayed.
                Maximum length for this field is 3000 characters.
            alt_text (required): A plain-text summary of the image. This should not contain any markup.
                Maximum length for this field is 2000 characters.
            title: An optional title for the image in the form of a text object that can only be of type: plain_text.
                Maximum length for the text in this field is 2000 characters.
            block_id: A string acting as a unique identifier for a block. If not specified, one will be generated.
                Maximum length for this field is 255 characters.
                block_id should be unique for each message and each iteration of a message.
                If a message is updated, use a new block_id.
        """
        super().__init__(type=self.type, block_id=block_id)
        show_unknown_key_warning(self, others)

        self.image_url = image_url
        self.alt_text = alt_text
        self.title = TextObject.parse(title)

    @JsonValidator(
        f"image_url attribute cannot exceed {image_url_max_length} characters"
    )
    def _validate_image_url_length(self):
        return len(self.image_url) <= self.image_url_max_length

    @JsonValidator(f"alt_text attribute cannot exceed {alt_text_max_length} characters")
    def _validate_alt_text_length(self):
        return len(self.alt_text) <= self.alt_text_max_length

    @JsonValidator(f"title attribute cannot exceed {title_max_length} characters")
    def _validate_title_length(self):
        return (
            self.title is None
            or self.title.text is None
            or len(self.title.text) <= self.title_max_length
        )


class ActionsBlock(Block):
    type = "actions"
    elements_max_length = 5

    @property
    def attributes(self) -> Set[str]:
        return super().attributes.union({"elements"})

    def __init__(
        self,
        *,
        elements: Sequence[Union[dict, InteractiveElement]],
        block_id: Optional[str] = None,
        **others: dict,
    ):
        """A block that is used to hold interactive elements.
        https://api.slack.com/reference/block-kit/blocks#actions

        Args:
            elements (required): An array of interactive element objects - buttons, select menus, overflow menus,
                or date pickers. There is a maximum of 5 elements in each action block.
            block_id: A string acting as a unique identifier for a block.
                If not specified, a block_id will be generated.
                You can use this block_id when you receive an interaction payload to identify the source of the action.
                Maximum length for this field is 255 characters.
                block_id should be unique for each message and each iteration of a message.
                If a message is updated, use a new block_id.
        """
        super().__init__(type=self.type, block_id=block_id)
        show_unknown_key_warning(self, others)

        self.elements = BlockElement.parse_all(elements)

    @JsonValidator(f"elements attribute cannot exceed {elements_max_length} elements")
    def _validate_elements_length(self):
        return self.elements is None or len(self.elements) <= self.elements_max_length


class ContextBlock(Block):
    type = "context"
    elements_max_length = 10

    @property
    def attributes(self) -> Set[str]:
        return super().attributes.union({"elements"})

    def __init__(
        self,
        *,
        elements: Sequence[Union[dict, ImageElement, TextObject]],
        block_id: Optional[str] = None,
        **others: dict,
    ):
        """Displays message context, which can include both images and text.
        https://api.slack.com/reference/block-kit/blocks#context

        Args:
            elements (required): An array of image elements and text objects. Maximum number of items is 10.
            block_id: A string acting as a unique identifier for a block. If not specified, one will be generated.
                Maximum length for this field is 255 characters.
                block_id should be unique for each message and each iteration of a message.
                If a message is updated, use a new block_id.
        """
        super().__init__(type=self.type, block_id=block_id)
        show_unknown_key_warning(self, others)

        self.elements = BlockElement.parse_all(elements)

    @JsonValidator(f"elements attribute cannot exceed {elements_max_length} elements")
    def _validate_elements_length(self):
        return self.elements is None or len(self.elements) <= self.elements_max_length


class InputBlock(Block):
    type = "input"
    label_max_length = 2000
    hint_max_length = 2000

    @property
    def attributes(self) -> Set[str]:
        return super().attributes.union(
            {"label", "hint", "element", "optional", "dispatch_action"}
        )

    def __init__(
        self,
        *,
        label: Union[str, dict, PlainTextObject],
        element: Union[str, dict, InputInteractiveElement],
        block_id: Optional[str] = None,
        hint: Optional[Union[str, dict, PlainTextObject]] = None,
        dispatch_action: Optional[bool] = None,
        optional: Optional[bool] = None,
        **others: dict,
    ):
        """A block that collects information from users - it can hold a plain-text input element,
        a select menu element, a multi-select menu element, or a datepicker.
        https://api.slack.com/reference/block-kit/blocks#input

        Args:
            label (required): A label that appears above an input element in the form of a text object
                that must have type of plain_text. Maximum length for the text in this field is 2000 characters.
            element (required): An plain-text input element, a checkbox element, a radio button element,
                a select menu element, a multi-select menu element, or a datepicker.
            block_id: A string acting as a unique identifier for a block. If not specified, one will be generated.
                Maximum length for this field is 255 characters.
                block_id should be unique for each message or view and each iteration of a message or view.
                If a message or view is updated, use a new block_id.
            hint: An optional hint that appears below an input element in a lighter grey.
                It must be a text object with a type of plain_text.
                Maximum length for the text in this field is 2000 characters.
            dispatch_action: A boolean that indicates whether or not the use of elements in this block
                should dispatch a block_actions payload. Defaults to false.
            optional: A boolean that indicates whether the input element may be empty when a user submits the modal.
                Defaults to false.
        """
        super().__init__(type=self.type, block_id=block_id)
        show_unknown_key_warning(self, others)

        self.label = TextObject.parse(label, default_type=PlainTextObject.type)
        self.element = BlockElement.parse(element)
        self.hint = TextObject.parse(hint, default_type=PlainTextObject.type)
        self.dispatch_action = dispatch_action
        self.optional = optional

    @JsonValidator(f"label attribute cannot exceed {label_max_length} characters")
    def _validate_label_length(self):
        return (
            self.label is None
            or self.label.text is None
            or len(self.label.text) <= self.label_max_length
        )

    @JsonValidator(f"hint attribute cannot exceed {hint_max_length} characters")
    def _validate_hint_length(self):
        return (
            self.hint is None
            or self.hint.text is None
            or len(self.hint.text) <= self.label_max_length
        )

    @JsonValidator(
        (
            "element attribute must be a string, select element, multi-select element, "
            "or a datepicker. (Sub-classes of InputInteractiveElement)"
        )
    )
    def _validate_element_type(self):
        return self.element is None or isinstance(
            self.element, (str, InputInteractiveElement)
        )


class FileBlock(Block):
    type = "file"

    @property
    def attributes(self) -> Set[str]:
        return super().attributes.union({"external_id", "source"})

    def __init__(
        self,
        *,
        external_id: str,
        source: str = "remote",
        block_id: Optional[str] = None,
        **others: dict,
    ):
        """Displays a remote file.
        https://api.slack.com/reference/block-kit/blocks#file

        Args:
            external_id (required): The external unique ID for this file.
            source (required): At the moment, source will always be remote for a remote file.
            block_id: A string acting as a unique identifier for a block. If not specified, one will be generated.
                Maximum length for this field is 255 characters.
                block_id should be unique for each message and each iteration of a message.
                If a message is updated, use a new block_id.
        """
        super().__init__(type=self.type, block_id=block_id)
        show_unknown_key_warning(self, others)

        self.external_id = external_id
        self.source = source


class CallBlock(Block):
    type = "call"

    @property
    def attributes(self) -> Set[str]:
        return super().attributes.union({"call_id", "api_decoration_available", "call"})

    def __init__(
        self,
        *,
        call_id: str,
        api_decoration_available: Optional[bool] = None,
        call: Optional[Dict[str, Dict[str, Any]]] = None,
        block_id: Optional[str] = None,
        **others: dict,
    ):
        """Displays a call information
        https://api.slack.com/reference/block-kit/blocks#call
        """
        super().__init__(type=self.type, block_id=block_id)
        show_unknown_key_warning(self, others)

        self.call_id = call_id
        self.api_decoration_available = api_decoration_available
        self.call = call


class HeaderBlock(Block):
    type = "header"
    text_max_length = 150

    @property
    def attributes(self) -> Set[str]:
        return super().attributes.union({"text"})

    def __init__(
        self,
        *,
        block_id: Optional[str] = None,
        text: Optional[Union[str, dict, TextObject]] = None,
        **others: dict,
    ):
        """A header is a plain-text block that displays in a larger, bold font.
        https://api.slack.com/reference/block-kit/blocks#header

        Args:
            block_id: A string acting as a unique identifier for a block. If not specified, one will be generated.
                Maximum length for this field is 255 characters.
                block_id should be unique for each message and each iteration of a message.
                If a message is updated, use a new block_id.
            text (required): The text for the block, in the form of a plain_text text object.
                Maximum length for the text in this field is 150 characters.
        """
        super().__init__(type=self.type, block_id=block_id)
        show_unknown_key_warning(self, others)

        self.text = TextObject.parse(text, default_type=PlainTextObject.type)

    @JsonValidator("text attribute must be specified")
    def _validate_text(self):
        return self.text is not None

    @JsonValidator(f"text attribute cannot exceed {text_max_length} characters")
    def _validate_alt_text_length(self):
        return self.text is None or len(self.text.text) <= self.text_max_length
