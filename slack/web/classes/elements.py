import string
from random import random
from typing import List, Union

from .objects import (
    ButtonStyle,
    ConfirmObject,
    JsonObject,
    Option,
    OptionGroup,
    OptionType,
    PlainTextObject,
)
from ...errors import SlackObjectFormationError


class BlockElement(JsonObject):
    def __init__(self, type: str):
        self.type = type

    def get_json(self) -> dict:
        return {"type": self.type}


class ImageElement(BlockElement):
    def __init__(self, image_url: str, alt_text: str):
        super().__init__(type="image")
        self.image_url = image_url
        self.alt_text = alt_text

    def get_json(self) -> dict:
        json = super().get_json()
        json["image_url"] = self.image_url
        json["alt_text"] = self.alt_text
        return json


class ButtonElement(BlockElement):
    def __init__(
        self,
        text: str,
        action_id: str,
        value: str,
        style: Union[ButtonStyle, str] = None,
        confirm: ConfirmObject = None,
    ):
        super().__init__(type="button")
        self.text = text
        self.action_id = action_id
        self.value = value
        self.style = self.get_raw_value(style)
        self.confirm = confirm

    def get_json(self) -> dict:
        if len(self.text) > 75:
            raise SlackObjectFormationError(
                "text attribute cannot exceed 75 characters"
            )
        if len(self.action_id) > 255:
            raise SlackObjectFormationError(
                "action_id attribute cannot exceed 255 characters"
            )
        if len(self.value) > 75:
            raise SlackObjectFormationError(
                "value attribute cannot exceed 75 characters"
            )
        if not ButtonStyle.contains(self.style):
            raise SlackObjectFormationError(
                "style attribute must be one of the following values: "
                f"{ButtonStyle.pretty_print()}"
            )
        json = super().get_json()
        json["text"] = PlainTextObject(self.text).get_json()
        json["action_id"] = self.action_id
        json["value"] = self.value
        if self.style is not None:
            json["style"] = self.style
        if self.confirm is not None:
            json["confirm"] = self.confirm.get_json()
        return json


class LinkButtonElement(ButtonElement):
    def __init__(self, text: str, url: str, style: str = None):
        random_id = "".join(random.choice(string.ascii_uppercase) for _ in range(16))
        super().__init__(text=text, action_id=random_id, value="", style=style)
        assert len(self.url) < 3000
        self.url = url

    def get_json(self) -> dict:
        if len(self.url) >= 3000:
            raise SlackObjectFormationError(
                "url attribute cannot exceed 3000 characters"
            )
        json = super().get_json()
        json["url"] = self.url
        return json


class DropdownElement(BlockElement):
    def __init__(
        self,
        placeholder: str,
        action_id: str,
        options: List[Union[Option, OptionGroup]],
        initial_option: Option = None,
        confirm: ConfirmObject = None,
    ):
        super().__init__(type="static_select")
        self.placeholder = placeholder
        self.action_id = action_id
        self.options = options
        self.initial_option = initial_option
        self.confirm = confirm

    def get_json(self) -> dict:
        if len(self.placeholder) > 150:
            raise SlackObjectFormationError(
                "placeholder attribute cannot exceed 150 characters"
            )
        if len(self.action_id) > 255:
            raise SlackObjectFormationError(
                "action_id attribute cannot exceed 255 characters"
            )
        if len(self.options) > 100:
            raise SlackObjectFormationError(
                "options attribute cannot exceed 100 elements"
            )
        json = super().get_json()
        json["placeholder"] = PlainTextObject(self.placeholder).get_json()
        json["action_id"] = self.action_id
        if isinstance(self.options[0], Option):
            json["options"] = [
                option.get_json(OptionType.BLOCK) for option in self.options
            ]
        else:
            json["option_groups"] = [
                option.get_json(OptionType.BLOCK) for option in self.options
            ]
        if self.initial_option is not None:
            json["initial_option"] = self.initial_option.get_json(OptionType.BLOCK)
        if self.confirm is not None:
            json["confirm"] = self.confirm.get_json()
        return json


class ExternalDropdownElement(BlockElement):
    def __init__(self):
        super().__init__(type="external_select")
        raise NotImplementedError("Stub")


class UserDropdownElement(BlockElement):
    def __init__(
        self,
        placeholder: str,
        action_id: str,
        initial_user: str = None,
        confirm: ConfirmObject = None,
    ):
        super().__init__(type="users_select")
        self.placeholder = placeholder
        self.action_id = action_id
        self.initial_user = initial_user
        self.confirm = confirm

    def get_json(self) -> dict:
        if len(self.placeholder) > 150:
            raise SlackObjectFormationError(
                "placeholder attribute cannot exceed 150 characters"
            )
        if len(self.action_id) > 255:
            raise SlackObjectFormationError(
                "action_id attribute cannot exceed 255 characters"
            )
        json = super().get_json()
        json["placeholder"] = PlainTextObject(self.placeholder).get_json()
        json["action_id"] = self.action_id
        if self.initial_user is not None:
            json["initial_user"] = self.initial_user
        if self.confirm is not None:
            json["confirm"] = self.confirm.get_json()
        return json


class ConversationDropdownElement(BlockElement):
    def __init__(
        self,
        placeholder: str,
        action_id: str,
        initial_conversation: str = None,
        confirm: ConfirmObject = None,
    ):
        super().__init__(type="conversations_select")
        self.placeholder = placeholder
        self.action_id = action_id
        self.initial_conversation = initial_conversation
        self.confirm = confirm

    def get_json(self) -> dict:
        if len(self.placeholder) > 150:
            raise SlackObjectFormationError(
                "placeholder attribute cannot exceed 150 characters"
            )
        if len(self.action_id) > 255:
            raise SlackObjectFormationError(
                "action_id attribute cannot exceed 255 characters"
            )
        json = super().get_json()
        json["placeholder"] = PlainTextObject(self.placeholder).get_json()
        json["action_id"] = self.action_id
        if self.initial_conversation is not None:
            json["initial_conversation"] = self.initial_conversation
        if self.confirm is not None:
            json["confirm"] = self.confirm.get_json()
        return json


class ChannelDropdownElement(BlockElement):
    def __init__(
        self,
        placeholder: str,
        action_id: str,
        initial_channel: str = None,
        confirm: ConfirmObject = None,
    ):
        super().__init__(type="channels_select")
        self.placeholder = placeholder
        self.action_id = action_id
        self.initial_channel = initial_channel
        self.confirm = confirm

    def get_json(self) -> dict:
        if len(self.placeholder) > 150:
            raise SlackObjectFormationError(
                "placeholder attribute cannot exceed 150 characters"
            )
        if len(self.action_id) > 255:
            raise SlackObjectFormationError(
                "action_id attribute cannot exceed 255 characters"
            )
        json = super().get_json()
        json["placeholder"] = PlainTextObject(self.placeholder).get_json()
        json["action_id"] = self.action_id
        if self.initial_channel is not None:
            json["initial_channel"] = self.initial_channel
        if self.confirm is not None:
            json["confirm"] = self.confirm.get_json()
        return json


class OverflowElement(BlockElement):
    def __init__(
        self, options: List[Option], action_id: str, confirm: ConfirmObject = None
    ):
        super().__init__(type="overflow")
        self.options = options
        self.action_id = action_id
        self.confirm = confirm

    def get_json(self) -> dict:
        if len(self.options) < 2 or len(self.options) > 5:
            raise SlackObjectFormationError(
                "options attribute must have between 2 and 5 items"
            )
        if len(self.action_id) > 255:
            raise SlackObjectFormationError(
                "action_id attribute cannot exceed 255 characters"
            )
        json = super().get_json()
        json["options"] = [option.get_json(OptionType.BLOCK) for option in self.options]
        json["action_id"] = self.action_id
        if self.confirm is not None:
            json["confirm"] = self.confirm.get_json()
        return json


class DatePickerElement(BlockElement):
    def __init__(
        self,
        placeholder: str,
        action_id: str,
        initial_date: str,
        confirm: ConfirmObject = None,
    ):
        super().__init__(type="datepicker")
        self.placeholder = placeholder
        self.action_id = action_id
        self.initial_date = initial_date
        self.confirm = confirm

    def get_json(self) -> dict:
        if len(self.placeholder) > 150:
            raise SlackObjectFormationError(
                "placeholder attribute cannot exceed 150 characters"
            )
        if len(self.action_id) > 255:
            raise SlackObjectFormationError(
                "action_id attribute cannot exceed 255 characters"
            )
        json = super().get_json()
        json["action_id"] = self.action_id
        if self.placeholder is not None:
            json["placeholder"] = PlainTextObject(self.placeholder).get_json()
        if self.initial_date is not None:
            json["initial_date"] = self.initial_date
        if self.confirm is not None:
            json["confirm"] = self.confirm.get_json()
        return json


SelectElements = Union[
    DropdownElement,
    ExternalDropdownElement,
    UserDropdownElement,
    ChannelDropdownElement,
    ConversationDropdownElement,
]

InteractiveElements = Union[
    ButtonElement, SelectElements, OverflowElement, DatePickerElement
]
