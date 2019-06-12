import re
import string
from abc import ABCMeta, abstractmethod
from random import random
from typing import List, Set, Union

from .objects import (
    ButtonStyles,
    ConfirmObject,
    EnumValidator,
    JsonObject,
    JsonValidator,
    Option,
    OptionGroup,
    OptionTypes,
    PlainTextObject,
    extract_json,
)


class BlockElement(JsonObject):
    attributes = {"type"}

    def __init__(self, *, type: str):
        self.type = type


class InteractiveElement(BlockElement):
    @property
    def attributes(self) -> Set[str]:
        return super().attributes.union({"action_id"})

    def __init__(self, *, action_id: str, type: str):
        super().__init__(type=type)
        self.action_id = action_id

    @JsonValidator("action_id attribute cannot exceed 255 characters")
    def action_id_length(self):
        return len(self.action_id) <= 255


class ImageElement(BlockElement):
    def __init__(self, *, image_url: str, alt_text: str):
        super().__init__(type="image")
        self.image_url = image_url
        self.alt_text = alt_text

    def get_json(self) -> dict:
        json = super().get_json()
        json["image_url"] = self.image_url
        json["alt_text"] = self.alt_text
        return json


class ButtonElement(InteractiveElement):
    @property
    def attributes(self) -> Set[str]:
        return super().attributes.union({"value", "style"})

    def __init__(
        self,
        *,
        text: str,
        action_id: str,
        value: str,
        style: str = None,
        confirm: ConfirmObject = None,
    ):
        super().__init__(action_id=action_id, type="button")
        self.text = text
        self.value = value
        self.style = style
        self.confirm = confirm

    @JsonValidator("text attribute cannot exceed 75 characters")
    def text_length(self):
        return len(self.text) <= 75

    @JsonValidator("value attribute cannot exceed 75 characters")
    def value_length(self):
        return len(self.value) <= 75

    @EnumValidator("style", ButtonStyles)
    def style_valid(self):
        return self.style is None or self.style in ButtonStyles

    def get_json(self) -> dict:
        json = super().get_json()
        json["text"] = PlainTextObject.from_string(self.text)
        if self.confirm is not None:
            json["confirm"] = extract_json(self.confirm, ConfirmObject)
        return json


class LinkButtonElement(ButtonElement):
    @property
    def attributes(self) -> Set[str]:
        return super().attributes.union({"url"})

    def __init__(self, *, text: str, url: str, style: str = None):
        random_id = "".join(random.choice(string.ascii_uppercase) for _ in range(16))
        super().__init__(text=text, action_id=random_id, value="", style=style)
        self.url = url

    @JsonValidator("url attribute cannot exceed 3000 characters")
    def url_length(self):
        return len(self.url) <= 3000


class AbstractSelector(InteractiveElement, metaclass=ABCMeta):
    def __init__(
        self,
        *,
        placeholder: str,
        action_id: str,
        type: str,
        confirm: ConfirmObject = None,
    ):
        super().__init__(action_id=action_id, type=type)
        self.placeholder = placeholder
        self.confirm = confirm

    @JsonValidator("placeholder attribute cannot exceed 150 characters")
    def placeholder_length(self):
        return len(self.placeholder) <= 150

    def get_json(self,) -> dict:
        json = super().get_json()
        json["placeholder"] = PlainTextObject.from_string(self.placeholder)
        if self.confirm is not None:
            json["confirm"] = extract_json(self.confirm, ConfirmObject)
        return json


class DropdownElement(AbstractSelector):
    def __init__(
        self,
        *,
        placeholder: str,
        action_id: str,
        options: List[Union[Option, OptionGroup]],
        initial_option: Option = None,
        confirm: ConfirmObject = None,
    ):
        super().__init__(
            placeholder=placeholder,
            action_id=action_id,
            type="static_select",
            confirm=confirm,
        )
        self.options = options
        self.initial_option = initial_option

    @JsonValidator("options attribute cannot exceed 100 items")
    def options_length(self):
        return len(self.options) <= 100

    def get_json(self) -> dict:
        json = super().get_json()
        if isinstance(self.options[0], Option):
            json["options"] = extract_json(self.options, OptionTypes, "text")
        else:
            json["option_groups"] = extract_json(self.options, OptionTypes, "text")
        if self.initial_option is not None:
            json["initial_option"] = extract_json(
                self.initial_option, OptionTypes, "text"
            )
        return json


class ExternalDropdownElement(AbstractSelector):
    @property
    def attributes(self) -> Set[str]:
        return super().attributes.union({"min_query_length"})

    def __init__(
        self,
        *,
        placeholder: str,
        action_id: str,
        initial_option: OptionTypes = None,
        min_query_length: int = None,
        confirm: ConfirmObject = None,
    ):
        super().__init__(
            action_id=action_id,
            type="external_select",
            placeholder=placeholder,
            confirm=confirm,
        )
        self.initial_option = initial_option
        self.min_query_length = min_query_length

    def get_json(self) -> dict:
        json = super().get_json()
        if self.initial_option is not None:
            json["initial_option"] = extract_json(
                self.initial_option, OptionTypes, "text"
            )
        return json


class AbstractDynamicDropdown(AbstractSelector, metaclass=ABCMeta):
    @property
    @abstractmethod
    def initial_object_type(self):
        pass

    def __init__(
        self,
        *,
        placeholder: str,
        action_id: str,
        initial_value: str = None,
        confirm: ConfirmObject = None,
    ):
        super().__init__(
            action_id=action_id,
            type=f"{self.initial_object_type}s_select",
            confirm=confirm,
            placeholder=placeholder,
        )
        self.initial_value = initial_value

    def get_json(self) -> dict:
        json = super().get_json()
        if self.initial_value is not None:
            json[f"initial_{self.initial_object_type}"] = self.initial_value
        return json


class UserDropdownElement(InteractiveElement):
    initial_object_type = "user"


class ConversationDropdownElement(BlockElement):
    initial_object_type = "conversation"


class ChannelDropdownElement(BlockElement):
    initial_object_type = "channel"


class OverflowElement(InteractiveElement):
    def __init__(
        self, *, options: List[Option], action_id: str, confirm: ConfirmObject = None
    ):
        super().__init__(action_id=action_id, type="overflow")
        self.options = options
        self.confirm = confirm

    @JsonValidator("options attribute must have between 2 and 5 items")
    def options_length(self):
        return 2 < len(self.options) <= 5

    def get_json(self) -> dict:
        json = super().get_json()
        json["options"] = extract_json(self.options, Option, "text")
        if self.confirm is not None:
            json["confirm"] = extract_json(self.confirm, ConfirmObject)
        return json


class DatePickerElement(AbstractSelector):
    @property
    def attributes(self) -> Set[str]:
        return super().attributes.union({"initial_date"})

    def __init__(
        self,
        *,
        action_id: str,
        placeholder: str = None,
        initial_date: str = None,
        confirm: ConfirmObject = None,
    ):
        super().__init__(
            action_id=action_id,
            type="datepicker",
            placeholder=placeholder,
            confirm=confirm,
        )
        self.initial_date = initial_date

    @JsonValidator("initial_date attribute must be in format 'YYYY-MM-DD'")
    def initial_date_valid(self):
        return self.initial_date is None or re.match(
            r"\d{4}-[01][12]-[0123]\d", self.initial_date
        )


SelectElements = Union[
    DropdownElement,
    ExternalDropdownElement,
    UserDropdownElement,
    ChannelDropdownElement,
    ConversationDropdownElement,
]
