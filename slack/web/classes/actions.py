from abc import ABCMeta, abstractmethod
from typing import Iterable, Set, Union

from .objects import (
    ButtonStyles,
    DynamicDropdownTypes,
    EnumValidator,
    JsonObject,
    JsonValidator,
    Option,
    OptionGroup,
    extract_json,
)


class Action(JsonObject):
    attributes = {"name", "text", "type", "url"}

    def __init__(self, *, text: str, type: str, name: str = None, url: str = None):
        self.name = name
        self.url = url
        self.text = text
        self.type = type

    @JsonValidator("name attribute is required")
    def name_or_url_present(self):
        return self.name is not None or self.url is not None


class ActionConfirmation(JsonObject):
    attributes = {"title", "text", "ok_text", "dismiss_text"}

    def __init__(
        self,
        *,
        text: str,
        title: str = None,
        ok_text: str = "Okay",
        dismiss_text: str = "Cancel",
    ):
        self.text = text
        self.title = title
        self.ok_text = ok_text
        self.dismiss_text = dismiss_text


class Button(Action):
    @property
    def attributes(self):
        return super().attributes.union({"value", "style"})

    def __init__(
        self,
        *,
        name: str,
        text: str,
        value: str,
        confirm: ActionConfirmation = None,
        style: str = None,
    ):
        """
        Simple button for use inside attachments

        :param name: name of the element, important for interactive buttons

        :param text: text to display on the button

        :param value: the internal value to send on interaction

        :param confirm: an ActionConfirmation object

        :param style: "primary" or "danger" to represent important buttons
        """
        super().__init__(name=name, text=text, type="button")
        self.value = value
        self.confirm = confirm
        self.style = style

    @EnumValidator("style", ButtonStyles)
    def style_valid(self):
        return self.style is None or self.style in ButtonStyles

    def get_json(self) -> dict:
        json = super().get_json()
        if self.confirm is not None:
            json["confirm"] = extract_json(self.confirm, ActionConfirmation)
        return json


class LinkButton(Action):
    def __init__(self, *, text: str, url: str):
        """
        A simple interactive button that just opens a URL

        :param text: text to display on the button, eg 'Click Me!"

        :param url: the URL to open
        """
        super().__init__(text=text, url=url, type="button")


class MessageDropdown(Action, metaclass=ABCMeta):
    @property
    def attributes(self) -> Set[str]:
        return super().attributes.union(
            {"name", "text", "value", "type", "data_source"}
        )

    @property
    @abstractmethod
    def property_key(self) -> str:
        pass

    @property
    @abstractmethod
    def data_source(self) -> str:
        pass

    def __init__(
        self,
        *,
        name: str,
        text: str,
        options: Iterable[Union[Option, OptionGroup]] = None,
        selected_option: Union[Option, OptionGroup] = None,
    ):
        super().__init__(text=text, name=name, type="select")
        if self.data_source != "static":
            self.options = list(options)
        else:
            self.options = None
        self.selected_option = selected_option

    @JsonValidator("options attribute cannot exceed 100 items")
    def options_length(self):
        return self.data_source != "static" or len(self.options) < 100

    def get_json(self) -> dict:
        json = super().get_json()
        if self.data_source != "static":
            json[self.property_key] = extract_json(self.options, OptionGroup, "label")
        return json


class OptionsMessageDropdown(MessageDropdown):
    data_source = "static"
    property_key = "options"

    def __init__(self, *, name: str, text: str, options: Iterable[Option], **kwargs):
        super().__init__(name=name, text=text, options=options, **kwargs)


class OptionGroupMessageDropdown(MessageDropdown):
    data_source = "static"
    property_key = "options_group"

    def __init__(
        self, *, name: str, text: str, options: Iterable[OptionGroup], **kwargs
    ):
        super().__init__(name=name, text=text, options=options, **kwargs)


class DynamicMessageDropdown(MessageDropdown):
    property_key = "options"

    def __init__(self, *, name: str, text: str, source: str, **kwargs):
        super().__init__(name=name, text=text, **kwargs)
        self._source = source

    @property
    def data_source(self) -> str:
        return self._source

    @EnumValidator("source", DynamicDropdownTypes)
    def source_valid(self):
        return self._source in DynamicDropdownTypes


class ExternalMessageDropdown(MessageDropdown):
    data_source = "external"
    property_key = "options"

    @property
    def attributes(self) -> Set[str]:
        return super().attributes.union({"min_query_length"})

    def __init__(
        self,
        *,
        name: str,
        label: str,
        selected_option: Option = None,
        min_query_length: int = None,
        **kwargs,
    ):
        super().__init__(name=name, text=label, **kwargs)
        self.selected_option = selected_option
        self.min_query_length = min_query_length

    def get_json(self) -> dict:
        json = super().get_json()
        if self.selected_option is not None:
            # selected_option JSON must be a list, even though it will only be one item
            json["selected_option"] = extract_json(
                [self.selected_option], Option, "label"
            )
        return json
