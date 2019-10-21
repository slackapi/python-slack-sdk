from . import JsonObject, JsonValidator, extract_json
from .elements import PlainTextObject

from typing import List, Optional, Union

from .blocks import (
    Block,
    BlockElement,
    SectionBlock,
    DividerBlock,
    ImageBlock,
    ActionsBlock,
    InteractiveElement,
    ContextBlock,
    InputBlock,
    AbstractSelector,
    FileBlock,
)
from .objects import TextObject


class ModalBuilder(JsonObject):
    """The ModalBuilder enables you to more easily construct the JSON required
    to create a modal in Slack.

    Modals are a focused surface to collect data from users
    or display dynamic and interactive information.

    To learn how modals are invoked, how to compose their contents,
    and how to enable and handle complex interactivity read this guide:

    https://api.slack.com/block-kit/surfaces/modals
    """

    _type: str
    _title: PlainTextObject
    _blocks: List[Block]
    _close: Optional[PlainTextObject]
    _submit: Optional[PlainTextObject]
    _private_metadata: Optional[str]
    _callback_id: Optional[str]
    _clear_on_close: Optional[bool]
    _notify_on_close: Optional[bool]
    _external_id: Optional[str]

    title_max_length = 24
    blocks_max_length = 100
    close_max_length = 24
    submit_max_length = 24
    private_metadata_max_length = 3000
    callback_id_max_length = 255

    attributes = {
        "_title",
        "_blocks",
        "_close",
        "_submit",
        "_private_metadata",
        "_callback_id",
        "_clear_on_close",
        "_notify_on_close",
        "_external_id",
    }

    def __init__(self):
        self._type = "modal"
        self._title = None
        self._blocks = []
        self._close = None
        self._submit = None
        self._private_metadata = None
        self._callback_id = None
        self._clear_on_close = False
        self._notify_on_close = False
        self._external_id = None

    def title(self, title: str) -> "ModalBuilder":
        """
        Specify a title for this modal

        Args:
          title: must not exceed 24 characters
        """
        self._title = PlainTextObject(text=title)
        return self

    def close(self, close: str) -> "ModalBuilder":
        """
        Specify the text displayed in the close button at the bottom-right of the view.

        Max length of 24 characters.

        Args:
          close: must not exceed 24 characters
        """
        self._close = PlainTextObject(text=close)
        return self

    def submit(self, submit: str) -> "ModalBuilder":
        """
        Specify the text displayed in the submit button at the bottom-right of the view.

        Important Note: submit is required when an input block is within the blocks array.

        Max length of 24 characters.

        Args:
          submit: must not exceed 24 characters
        """
        self._submit = PlainTextObject(text=submit)
        return self

    def private_metadata(self, private_metadata: str) -> "ModalBuilder":
        """An optional string that will be sent to your app in view_submission
        and block_actions events.

        Args:
          private_metadata: must not exceed 3000 characters
        """
        self._private_metadata = private_metadata
        return self

    def callback_id(self, callback_id: str) -> "ModalBuilder":
        """An identifier to recognize interactions and submissions of this particular modal.
        Don't use this to store sensitive information (use private_metadata instead).

        Args:
          callback_id: must not exceed 255 characters
        """
        self._callback_id = callback_id
        return self

    def clear_on_close(self, clear_on_close: bool) -> "ModalBuilder":
        """When set to true, clicking on the close button will clear
        all views in a modal and close it.

        Args:
          clear_on_close: Default is false.
        """
        self._clear_on_close = clear_on_close
        return self

    def notify_on_close(self, notify_on_close: bool) -> "ModalBuilder":
        """	Indicates whether Slack will send your request URL a view_closed
        event when a user clicks the close button.

        Args:
          notify_on_close: Default is false.
        """
        self._notify_on_close = notify_on_close
        return self

    def external_id(self, external_id: str) -> "ModalBuilder":
        """A custom identifier that must be unique for all views on a per-team basis.

        Args:
          external_id: A unique identifier.
        """
        self._external_id = external_id
        return self

    def section(
        self,
        *,
        text: Union[str, TextObject] = None,
        block_id: Optional[str] = None,
        fields: List[str] = None,
        accessory: Optional[BlockElement] = None,
    ) -> "ModalBuilder":
        """A section is one of the most flexible blocks available.
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
        self._blocks.append(
            SectionBlock(
                text=text, block_id=block_id, fields=fields, accessory=accessory
            )
        )
        return self

    def divider(self, *, block_id: Optional[str] = None):
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
        self._blocks.append(DividerBlock(block_id=block_id))
        return self

    def image(
        self,
        *,
        image_url: str,
        alt_text: str,
        title: Optional[str] = None,
        block_id: Optional[str] = None,
    ):
        """A simple image block, designed to make those cat photos really pop.

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
        self._blocks.append(
            ImageBlock(
                image_url=image_url, alt_text=alt_text, title=title, block_id=block_id
            )
        )
        return self

    def actions(
        self, *, elements: List[InteractiveElement], block_id: Optional[str] = None
    ):
        """A block that is used to hold interactive elements.

        https://api.slack.com/reference/block-kit/blocks#actions

        Args:
            elements: Up to 5 InteractiveElement objects - buttons, date pickers, etc
            block_id: ID to be used for this block - autogenerated if left blank.
                Cannot exceed 255 characters.
        """
        self._blocks.append(ActionsBlock(elements=elements, block_id=block_id))
        return self

    def context(
        self, *, elements: List[InteractiveElement], block_id: Optional[str] = None
    ):
        """Displays message context, which can include both images and text.

        https://api.slack.com/reference/block-kit/blocks#context

        Args:
            elements: Up to 10 ImageElements and TextObjects
            block_id: ID to be used for this block - autogenerated if left blank.
                Cannot exceed 255 characters.
        """
        self._blocks.append(ContextBlock(elements=elements, block_id=block_id))
        return self

    def input(
        self,
        *,
        label: str,
        element: Union[str, AbstractSelector],
        hint: Optional[str] = None,
        optional: Optional[bool] = False,
    ):
        """A block that collects information from users - it can hold a
        plain-text input element, a select menu element, a multi-select menu element,
        or a datepicker.

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
        self._blocks.append(
            InputBlock(label=label, element=element, hint=hint, optional=optional)
        )
        return self

    def file(
        self,
        *,
        external_id: str,
        source: str = "remote",
        block_id: Optional[str] = None,
    ):
        """Displays a remote file.

        https://api.slack.com/reference/block-kit/blocks#file
        """
        self._blocks.append(
            FileBlock(external_id=external_id, source=source, block_id=block_id)
        )
        return self

    @JsonValidator(f"title must be between 1 and {title_max_length} characters")
    def title_length(self):
        if self._title is not None:
            return len(self._title.text) <= self.title_max_length

        return False

    @JsonValidator(f"modals must contain between 1 and {blocks_max_length} blocks")
    def blocks_length(self):
        return 0 < len(self._blocks) <= self.blocks_max_length

    @JsonValidator(f"close cannot exceed {close_max_length} characters")
    def close_length(self):
        if self._close is not None:
            return len(self._close.text) <= self.close_max_length

        return True

    @JsonValidator(f"submit cannot exceed {submit_max_length} characters")
    def submit_length(self):
        if self._submit is not None:
            return len(self._submit.text) <= self.submit_max_length

        return True

    @JsonValidator(
        f"submit is required when an 'input' block is within the blocks array"
    )
    def submit_required_when_input_block_used(self):
        if self._submit is None:
            return InputBlock not in [b.__class__ for b in self._blocks]

        return True

    @JsonValidator(
        f"private_metadata cannot exceed {private_metadata_max_length} characters"
    )
    def private_metadata_max_length(self):
        if self._private_metadata is None:
            return True

        return len(self._private_metadata) <= self.private_metadata_max_length

    @JsonValidator(f"callback_id cannot exceed {callback_id_max_length} characters")
    def callback_id_max_length(self):
        if self._callback_id is None:
            return True

        return len(self._callback_id) <= self.callback_id_max_length

    def to_dict(self) -> dict:
        self.validate_json()

        fields = {
            "type": self._type,
            "title": extract_json(self._title),
            "blocks": extract_json(self._blocks),
            "close": extract_json(self._close),
            "submit": extract_json(self._submit),
            "private_metadata": self._private_metadata,
            "callback_id": self._callback_id,
            "clear_on_close": self._clear_on_close,
            "notify_on_close": self._notify_on_close,
            "external_id": self._external_id,
        }

        return {k: v for k, v in fields.items() if v is not None}
