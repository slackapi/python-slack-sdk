from . import JsonObject, JsonValidator
from .elements import PlainTextObject
from .blocks import Block

from typing import List, Optional


class ModalBuilder(JsonObject):
    """The ModalBuilder enables you to more easily construct the JSON required
    to create a modal in Slack.

    A modal is a UI container that holds one to many views.

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

    # TODO: Add Builder Methods.

    @JsonValidator("type attribute must be set to modal")
    def type_equals_modal(self):
        return self._type == "modal"

    @JsonValidator(f"title cannot exceed {title_max_length} characters")
    def title_length(self):
        return len(self._title.text) <= self.title_max_length

    @JsonValidator(f"modals must contain between 1 and {blocks_max_length} blocks")
    def blocks_length(self):
        return 0 < len(self._blocks) <= self.blocks_max_length

    @JsonValidator(f"close cannot exceed {close_max_length} characters")
    def close_length(self):
        return len(self._close.text) <= self.close_max_length

    @JsonValidator(f"submit cannot exceed {submit_max_length} characters")
    def submit_length(self):
        return len(self._submit.text) <= self.submit_max_length

    @JsonValidator(
        f"submit is required when an 'input' block is within the blocks array"
    )
    def submit_required_when_input_block_used(self):
        # TODO: Add Validation
        # Get the list of the classes in the blocks array.
        # if input class is in the array: Ensure Submit is NOT None.
        pass

    @JsonValidator(
        f"private_metadata cannot exceed {private_metadata_max_length} characters"
    )
    def private_metadata_max_length(self):
        return len(self.private_metadata) <= self.private_metadata_max_length

    @JsonValidator(f"callback_id cannot exceed {callback_id_max_length} characters")
    def callback_id_max_length(self):
        return len(self.callback_id) <= self.callback_id_max_length

    # TODO: Add to_dict method.
