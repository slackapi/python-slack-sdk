from abc import ABCMeta, abstractmethod
from json import dumps
from typing import Iterable, List, Optional, Set, Union

from .objects import (
    DynamicDropdownTypes,
    EnumValidator,
    JsonObject,
    JsonValidator,
    Option,
    OptionGroup,
    OptionTypes,
    extract_json,
)

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
        "subtype",
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

    @JsonValidator("name attribute cannot exceed 300 characters")
    def name_length(self):
        return len(self.name) < 300

    @JsonValidator("label attribute cannot exceed 48 characters")
    def label_length(self):
        return len(self.label) < 48

    @JsonValidator("placeholder attribute cannot exceed 150 characters")
    def placeholder_length(self):
        return self.placeholder is None or len(self.placeholder) < 150

    @JsonValidator("hint attribute cannot exceed 150 characters")
    def hint_length(self):
        return self.hint is None or len(self.hint) < 150

    @JsonValidator(f"value attribute exceeded bounds")
    def value_length(self):
        return self.value is None or len(self.value) < self.max_value_length

    @JsonValidator("min_length attribute must be greater than or equal to 0")
    def min_length_above_zero(self):
        return self.min_length is None or self.min_length >= 0

    @JsonValidator(f"min_length attribute exceed bounds")
    def min_length_length(self):
        return self.min_length is None or self.min_length <= self.max_value_length

    @JsonValidator(f"min_length attribute must be less than max value attribute")
    def min_length_below_max_length(self):
        return self.min_length is None or self.min_length < self.max_length

    @JsonValidator("max_length attribute must be greater than or equal to 0")
    def max_length_above_zero(self):
        return self.max_length is None or self.max_length > 0

    @JsonValidator(f"max_length attribute exceeded bounds")
    def max_length_length(self):
        return self.max_length is None or self.max_length <= self.max_value_length

    @EnumValidator("subtype", DialogSubTypes)
    def subtype_valid(self):
        return self.subtype is None or self.subtype in DialogSubTypes

    def get_json(self) -> dict:
        json = super().get_json()
        json["type"] = self.element_type
        return json


class DialogTextFieldComponent(DialogTextComponent):
    element_type = "text"
    max_value_length = 150


class DialogTextAreaComponent(DialogTextComponent):
    element_type = "textarea"
    max_value_length = 3000


class DialogDropdown(JsonObject, metaclass=ABCMeta):
    attributes = {
        "name",
        "value",
        "label",
        "optional",
        "placeholder",
        "type",
        "data_source",
    }

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

    @JsonValidator("options attribute cannot exceed 100 items")
    def options_length(self):
        return self.data_source != "static" or len(self.options) < 100

    def get_json(self) -> dict:
        json = super().get_json()
        if self.data_source == "static":
            json[self.property_key] = extract_json(self.options, OptionTypes, "label")
        return json


class StaticDialogDropdown(DialogDropdown):
    data_source = "static"
    property_key = "options"

    def __init__(self, *, name: str, label: str, options: Iterable[Option], **kwargs):
        super().__init__(name=name, label=label, options=options, **kwargs)


class GroupedDialogDropdown(DialogDropdown):
    data_source = "static"
    property_key = "options_group"

    def __init__(
        self, *, name: str, label: str, options: Iterable[OptionGroup], **kwargs
    ):
        super().__init__(name=name, label=label, options=options, **kwargs)


class DynamicDialogDropdown(DialogDropdown):
    property_key = "options"

    def __init__(self, *, name: str, label: str, source: str, **kwargs):
        self.source = source
        super().__init__(name=name, label=label, **kwargs)

    @property
    def data_source(self) -> str:
        return self.source

    @EnumValidator("source", DynamicDropdownTypes)
    def source__valid(self):
        return self.source in DynamicDropdownTypes


class ExternalDialogDropdown(DialogDropdown):
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
        super().__init__(name=name, label=label, **kwargs)
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


class DialogBuilder(JsonObject):
    _callback_id: Optional[str]
    _elements: List[Union[DialogTextComponent, DialogDropdown]]
    _submit_label: Optional[str]
    _notify_on_cancel: bool
    _state: Optional[str]

    def __init__(self):
        self._title = None
        self._callback_id = None
        self._elements = []
        self._submit_label = None
        self._notify_on_cancel = False
        self._state = None

    def title(self, title: str) -> "DialogBuilder":
        """
        Specify a title for this dialog

        :param title: must not exceed 24 characters
        """
        self._title = title
        return self

    def state(self, state: Union[dict, str]) -> "DialogBuilder":
        """
        Pass state into this dialog - dictionaries will be automatically formatted to
        JSON

        :param state: Extra state information that you need to pass from this dialog
        back to your application on submission
        """
        if isinstance(state, dict):
            self._state = dumps(state)
        else:
            self._state = state
        return self

    def callback_id(self, callback_id: str) -> "DialogBuilder":
        """
        Specify a callback ID for this dialog, which your application will then
        receive upon dialog submission

        :param callback_id: a string identify this particular dialog
        """
        self._callback_id = callback_id
        return self

    def submit_label(self, label: str) -> "DialogBuilder":
        """
        The label to use on the 'Submit' button on the dialog. Defaults to 'Submit'
        if not specified.

        :param label: must not exceed 24 characters, and must be a single word (no
        spaces)
        """
        self._submit_label = label
        return self

    def notify_on_cancel(self, notify: bool) -> "DialogBuilder":
        """
        Whether this dialog should send a request to your application even if the
        user cancels their interaction. Defaults to False.

        :param notify: Set to True to indicate that your application should receive a
        request even if the user cancels interaction with the dialog.
        """
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

    @JsonValidator("title attribute is required")
    def title_present(self):
        return self._title is not None

    @JsonValidator("title attribute cannot exceed 24 characters")
    def title_length(self):
        return self._title is not None and len(self._title) <= 24

    @JsonValidator("callback_id attribute is required")
    def callback_id_present(self):
        return self._callback_id is not None

    @JsonValidator("dialogs must contain between 1 and 10 elements")
    def elements_length(self):
        return 0 < len(self._elements) <= 10

    @JsonValidator("submit_label cannot exceed 24 characters")
    def submit_label_length(self):
        return self._submit_label is None or len(self._submit_label) <= 24

    @JsonValidator("submit_label can only be one word")
    def submit_label_valid(self):
        return self._submit_label is None or " " not in self._submit_label

    @JsonValidator("state cannot exceed 3000 characters")
    def state_length(self):
        return not self._state or len(self._state) <= 3000

    def build(self) -> dict:
        self.validate_json()
        json = {
            "title": self._title,
            "callback_id": self._callback_id,
            "elements": extract_json(self._elements, JsonObject),
            "notify_on_cancel": self._notify_on_cancel,
        }
        if self._submit_label is not None:
            json["submit_label"] = self._submit_label
        if self._state is not None:
            json["state"] = self._state
        return json
