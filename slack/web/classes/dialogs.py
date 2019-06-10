from abc import ABCMeta, abstractmethod
from json import dumps
from typing import Iterable, List, Optional, Union

from .objects import BaseObject, DynamicDropdownTypes, JsonObject, Option, OptionGroup
from ...errors import SlackObjectFormationError

DialogSubTypes = {"email", "number", "tel", "url"}


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
        subtype: str = None,
    ):
        self.name = name
        self.label = label
        self.optional = optional
        self.placeholder = placeholder
        self.hint = hint
        self.value = value
        self.min_length = min_length
        self.max_length = max_length or self.max_value_length
        self.subtype = subtype

    def get_json(self) -> dict:
        if len(self.name) > 300:
            raise SlackObjectFormationError(
                "name attribute cannot exceed 300 characters"
            )
        if len(self.label) > 48:
            raise SlackObjectFormationError(
                "label attribute cannot exceed 48 characters"
            )
        if self.placeholder is not None and len(self.placeholder) > 150:
            raise SlackObjectFormationError(
                "placeholder attribute cannot exceed 150 characters"
            )
        if self.hint is not None and len(self.hint) > 150:
            raise SlackObjectFormationError(
                "hint attribute cannot exceed 150 characters"
            )
        if self.value is not None and len(self.value) > self.max_value_length:
            raise SlackObjectFormationError(
                f"value attribute cannot exceed {self.max_value_length} characters"
            )
        if self.min_length is not None:
            if 0 > self.min_length:
                raise SlackObjectFormationError(
                    "min_length attribute must be greater than 0"
                )
            elif self.min_length > self.max_value_length:
                raise SlackObjectFormationError(
                    f"min_length attribute must be less than {self.max_value_length}"
                )
        if self.max_length is not None:
            if 0 > self.max_length:
                raise SlackObjectFormationError(
                    "max_length attribute must be greater than 0"
                )
            elif self.max_length > self.max_value_length:
                raise SlackObjectFormationError(
                    f"max_length attribute must be less than {self.max_value_length}"
                )
        if self.subtype not in DialogSubTypes:
            raise SlackObjectFormationError(
                "subtype attribute must be one of the following values: "
                f"{', '.join(DialogSubTypes)}"
            )
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
        else:
            self.options = None
        self.optional = optional
        self.value = value
        self.placeholder = placeholder

    def get_json(self) -> dict:
        json = self.get_non_null_keys(self.attributes)
        if self.data_source == "static":
            if self.options > 100:
                raise SlackObjectFormationError(
                    "options attribute cannot exceed 100 items"
                )
            json[self.property_key] = [o.get_json("label") for o in self.options]
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

    def __init__(self, name: str, label: str, source: str, **kwargs):
        self.source = source
        super().__init__(name=name, label=label, **kwargs)

    @property
    def data_source(self) -> str:
        return self.source

    def get_json(self) -> dict:
        if self.source not in DynamicDropdownTypes:
            raise SlackObjectFormationError(
                "source attribute must be one of the following values: "
                f"{', '.join(DynamicDropdownTypes)}"
            )
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
        **kwargs,
    ):
        super().__init__(name, label, **kwargs)
        self.selected_option = selected_option
        self.min_query_length = min_query_length

    def get_json(self) -> dict:
        json = super().get_json()
        if self.min_query_length is not None:
            json["min_query_length"] = self.min_query_length
        if self.selected_option is not None:
            json["selected_option"] = [self.selected_option.get_json("label")]
        return json


class DialogBuilder(BaseObject):
    _callback_id: Optional[str]
    _elements: List[Union[DialogTextComponent, DialogDropdown]]
    _submit_label: Optional[str]
    _notify_on_cancel: bool
    _state: dict

    def __init__(self):
        self._title = None
        self._callback_id = None
        self._elements = []
        self._submit_label = None
        self._notify_on_cancel = False
        self._state = {}

    def title(self, title: str) -> "DialogBuilder":
        self._title = title
        return self

    def state(self, state: dict) -> "DialogBuilder":
        self._state = state
        return self

    def callback_id(self, callback_id: str) -> "DialogBuilder":
        self._callback_id = callback_id
        return self

    def submit_label(self, label: str) -> "DialogBuilder":
        self._submit_label = label
        return self

    def notify_on_cancel(self, notify: bool) -> "DialogBuilder":
        self._notify_on_cancel = notify
        return self

    def text_field(
        self,
        *,
        name: str,
        label: str,
        optional: bool = False,
        placeholder: str = None,
        hint: str = None,
        value: str = None,
        min_length: int = 0,
        max_length: int = None,
        subtype: str = None,
    ) -> "DialogBuilder":
        self._elements.append(
            DialogTextFieldComponent(
                name=name,
                label=label,
                optional=optional,
                placeholder=placeholder,
                hint=hint,
                value=value,
                min_length=min_length,
                max_length=max_length,
                subtype=subtype,
            )
        )
        return self

    def text_area(
        self,
        *,
        name: str,
        label: str,
        optional: bool = False,
        placeholder: str = None,
        hint: str = None,
        value: str = None,
        min_length: int = 0,
        max_length: int = None,
        subtype: str = None,
    ) -> "DialogBuilder":
        self._elements.append(
            DialogTextAreaComponent(
                name=name,
                label=label,
                optional=optional,
                placeholder=placeholder,
                hint=hint,
                value=value,
                min_length=min_length,
                max_length=max_length,
                subtype=subtype,
            )
        )
        return self

    def dropdown(
        self,
        *,
        name: str,
        label: str,
        options: Iterable[Union[Option, OptionGroup]],
        optional: bool = False,
        value: str = None,
        placeholder: str = None,
    ) -> "DialogBuilder":
        self._elements.append(
            DialogDropdown(
                name=name,
                label=label,
                options=options,
                optional=optional,
                value=value,
                placeholder=placeholder,
            )
        )
        return self

    def auto_dropdown(
        self,
        *,
        name: str,
        label: str,
        source: str,
        optional: bool = False,
        value: str = None,
        placeholder: str = None,
    ) -> "DialogBuilder":
        self._elements.append(
            DynamicDialogDropdown(
                name=name,
                label=label,
                source=source,
                optional=optional,
                value=value,
                placeholder=placeholder,
            )
        )
        return self

    def build(self) -> dict:
        if self._title is None:
            raise SlackObjectFormationError("title attribute is required")
        if len(self._title) > 24:
            raise SlackObjectFormationError(
                "title attribute cannot exceed 24 characters"
            )
        if self._callback_id is None:
            raise SlackObjectFormationError("callback_id attribute is required")
        if not 0 < len(self._elements) <= 10:
            raise SlackObjectFormationError(
                "dialogs must contain between 1 and 10 elements"
            )
        json = {
            "title": self._title,
            "callback_id": self._callback_id,
            "elements": [
                elem.get_json() if isinstance(elem, JsonObject) else elem
                for elem in self._elements
            ],
            "notify_on_cancel": self._notify_on_cancel,
        }
        if self.submit_label is not None:
            json["submit_label"] = self._submit_label
        json["state"] = dumps(self._state)
        return json
