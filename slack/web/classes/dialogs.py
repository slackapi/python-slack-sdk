from abc import ABCMeta, abstractmethod
from json import dumps
from typing import Iterable, List, Optional, Union

from .objects import (
    BaseObject,
    ContainerEnum,
    DynamicTypes,
    JsonObject,
    Option,
    OptionGroup,
    OptionType,
)


class DialogSubTypes(ContainerEnum):
    EMAIL = "email"
    NUMBER = "number"
    TELEPHONE = "tel"
    URL = "url"


class DialogTextComponent(JsonObject, metaclass=ABCMeta):
    attributes = {
        "optional",
        "name",
        "hint",
        "max_length",
        "value",
        "placeholder",
        "min_length",
        "label",
    }

    @property
    @abstractmethod
    def element_type(self):
        pass

    @property
    @abstractmethod
    def max_value_length(self):
        pass

    def __init__(
        self,
        name: str,
        label: str,
        optional: bool = False,
        placeholder: str = None,
        hint: str = None,
        value: str = None,
        min_length: int = 0,
        max_length: int = None,
        subtype: Union[DialogSubTypes, str] = None,
    ):
        assert len(name) <= 300, "Name exceeds max length"
        self.name = name
        assert len(label) <= 48, "Label exceeds max length"
        self.label = label
        self.optional = optional
        assert (
            placeholder is None or len(placeholder) <= 150
        ), "Placeholder exceeds max length"
        self.placeholder = placeholder
        assert hint is None or len(hint) <= 150, "Hint exceeds max length"
        self.hint = hint
        assert (
            value is None or len(value) <= self.max_value_length
        ), "Value exceeds max length"
        self.value = value
        assert (
            min_length is None or 0 <= min_length < self.max_value_length
        ), "Invalid min length"
        self.min_length = min_length
        assert (
            max_length is None or 0 < max_length <= self.max_value_length
        ), "Invalid max length"
        self.max_length = max_length or self.max_value_length
        subtype = self.get_raw_value(subtype, DialogSubTypes)
        assert subtype is None or DialogSubTypes.contains(subtype), "Invalid subtype"
        self.subtype = subtype

    def get_json(self) -> dict:
        json = self.get_non_null_keys(self.attributes)
        json["type"] = self.element_type
        if self.subtype is not None:
            json["subtype"] = self.subtype
        return json


class DialogTextFieldComponent(DialogTextComponent):
    element_type = "text"
    max_value_length = 150


class DialogTextAreaComponent(DialogTextComponent):
    element_type = "textarea"
    max_value_length = 3000


class DialogDropdown(JsonObject, metaclass=ABCMeta):
    attributes = {"name", "value", "label", "optional", "placeholder", "type"}

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
        name: str,
        label: str,
        options: Iterable[Union[Option, OptionGroup]] = None,
        optional: bool = False,
        value: str = None,
        placeholder: str = None,
    ):
        self.name = name
        self.label = label
        self.type = "select"
        if self.data_source == "static":
            self.options = list(options)
            assert 0 < len(self.options) <= 100
        else:
            self.options = None
        self.optional = optional
        self.value = value
        self.placeholder = placeholder

    def get_json(self) -> dict:
        json = self.get_non_null_keys(self.attributes)
        if self.data_source == "static":
            json[self.property_key] = [
                o.get_json(OptionType.DIALOG) for o in self.options
            ]
        json["data_source"] = self.data_source
        return json


class StaticDialogDropdown(DialogDropdown):
    data_source = "static"
    property_key = "options"

    def __init__(self, name: str, label: str, options: Iterable[Option], **kwargs):
        super().__init__(name=name, label=label, options=options, **kwargs)


class GroupedDialogDropdown(DialogDropdown):
    data_source = "static"
    property_key = "options_group"

    def __init__(self, name: str, label: str, options: Iterable[OptionGroup], **kwargs):
        super().__init__(name=name, label=label, options=options, **kwargs)


class DynamicDialogDropdown(DialogDropdown):
    property_key = "options"

    def __init__(
        self, name: str, label: str, source: Union[DynamicTypes, str], **kwargs
    ):
        source = self.get_raw_value(source, DynamicTypes)
        assert DynamicTypes.contains(source), "Invalid dynamic dropdown source"
        self.source = source
        super().__init__(name=name, label=label, **kwargs)

    @property
    def data_source(self) -> str:
        return self.source

    def get_json(self) -> dict:
        json = super().get_json()
        return json


class ExternalDialogDropdown(DialogDropdown):
    data_source = "external"
    property_key = "options"

    def __init__(
        self,
        name: str,
        label: str,
        selected_option: Option = None,
        min_query_length: int = None,
        **kwargs
    ):
        super().__init__(name, label, **kwargs)
        self.selected_option = selected_option
        self.min_query_length = min_query_length

    def get_json(self) -> dict:
        json = super().get_json()
        if self.min_query_length is not None:
            json["min_query_length"] = self.min_query_length
        if self.selected_option is not None:
            json["selected_option"] = [self.selected_option.get_json(OptionType.DIALOG)]
        return json


class DialogBuilder(BaseObject):
    _callback_id: Optional[str]
    _trigger_id: Optional[str]
    _elements: List[Union[DialogTextComponent, DialogDropdown]]
    _submit_label: Optional[str]
    _notify_on_cancel: bool
    _state: dict

    def __init__(self):
        self._title = None
        self._callback_id = None
        self._trigger_id = None
        self._elements = []
        self._submit_label = None
        self._notify_on_cancel = False
        self._state = {}

    def title(self, title: str):
        assert len(title) <= 24
        self._title = title
        return self

    def state(self, state: dict):
        self._state = state
        return self

    def callback_id(self, callback_id: str):
        self._callback_id = callback_id
        return self

    def trigger_id(self, trigger_id: str):
        self._trigger_id = trigger_id
        return self

    def submit_label(self, label: str):
        self._submit_label = label
        return self

    def notify_on_cancel(self, notify: bool):
        self._notify_on_cancel = notify
        return self

    def text_field(self, name: str, label: str, **kwargs):
        assert len(self._elements) < 10
        self._elements.append(DialogTextFieldComponent(name, label, **kwargs))
        return self

    def text_area(self, name: str, label: str, **kwargs):
        assert len(self._elements) < 10
        self._elements.append(DialogTextAreaComponent(name, label, **kwargs))
        return self

    def dropdown(
        self,
        name: str,
        label: str,
        options: Iterable[Union[Option, OptionGroup]],
        **kwargs
    ):
        assert len(self._elements) < 10
        self._elements.append(DialogDropdown(name, label, options, **kwargs))
        return self

    def auto_dropdown(
        self, name: str, label: str, auto_type: Union[DynamicTypes, str], **kwargs
    ):
        assert len(self._elements) < 10
        self._elements.append(DynamicDialogDropdown(name, label, auto_type, **kwargs))
        return self

    def build(self) -> (str, dict):
        assert self._title is not None
        assert self._callback_id is not None
        assert self._trigger_id is not None
        assert 0 < len(self._elements) <= 10
        json = {
            "title": self._title,
            "trigger_id": self._trigger_id,
            "callback_id": self._callback_id,
            "elements": [elem.get_json() for elem in self._elements],
            "notify_on_cancel": self._notify_on_cancel,
        }
        if self.submit_label is not None:
            json["submit_label"] = self._submit_label
        json["state"] = dumps(self._state)
        return self._trigger_id, json
