from abc import ABCMeta, abstractmethod
from typing import List, Optional, Set, Union

from . import EnumValidator, JsonObject, JsonValidator, extract_json
from .objects import DynamicSelectElementTypes, Option, OptionGroup

TextElementSubtypes = {"email", "number", "tel", "url"}


class DialogTextComponent(JsonObject, metaclass=ABCMeta):
    attributes = {
        "hint",
        "label",
        "max_length",
        "min_length",
        "name",
        "optional",
        "placeholder",
        "subtype",
        "type",
        "value",
    }

    name_max_length = 300
    label_max_length = 48
    placeholder_max_length = 150
    hint_max_length = 150

    @property
    @abstractmethod
    def type(self):
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
        placeholder: Optional[str] = None,
        hint: Optional[str] = None,
        value: Optional[str] = None,
        min_length: int = 0,
        max_length: Optional[int] = None,
        subtype: Optional[str] = None,
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

    @JsonValidator(f"name attribute cannot exceed {name_max_length} characters")
    def name_length(self):
        return len(self.name) < self.name_max_length

    @JsonValidator(f"label attribute cannot exceed {label_max_length} characters")
    def label_length(self):
        return len(self.label) < self.label_max_length

    @JsonValidator(
        f"placeholder attribute cannot exceed {placeholder_max_length} characters"
    )
    def placeholder_length(self):
        return (
            self.placeholder is None
            or len(self.placeholder) < self.placeholder_max_length
        )

    @JsonValidator(f"hint attribute cannot exceed {hint_max_length} characters")
    def hint_length(self):
        return self.hint is None or len(self.hint) < self.hint_max_length

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

    @EnumValidator("subtype", TextElementSubtypes)
    def subtype_valid(self):
        return self.subtype is None or self.subtype in TextElementSubtypes


class DialogTextField(DialogTextComponent):
    """
    Text elements are single-line plain text fields.

    https://api.slack.com/dialogs#text_elements
    """

    type = "text"
    max_value_length = 150


class DialogTextArea(DialogTextComponent):
    """
    A textarea is a multi-line plain text editing control. You've likely encountered
    these on the world wide web. Use this element if you want a relatively long
    answer from users. The element UI provides a remaining character count to the
    max_length you have set or the default, 3000.

    https://api.slack.com/dialogs#textarea_elements
    """

    type = "textarea"
    max_value_length = 3000


class AbstractDialogSelector(JsonObject, metaclass=ABCMeta):
    DataSourceTypes = DynamicSelectElementTypes.union({"external", "static"})

    attributes = {"data_source", "label", "name", "optional", "placeholder", "type"}

    name_max_length = 300
    label_max_length = 48
    placeholder_max_length = 150

    @property
    @abstractmethod
    def data_source(self) -> str:
        pass

    def __init__(
        self,
        *,
        name: str,
        label: str,
        optional: bool = False,
        value: Union[Option, str] = None,
        placeholder: str = None,
    ):
        self.name = name
        self.label = label
        self.optional = optional
        self.value = value
        self.placeholder = placeholder
        self.type = "select"

    @JsonValidator(f"name attribute cannot exceed {name_max_length} characters")
    def name_length(self):
        return len(self.name) < self.name_max_length

    @JsonValidator(f"label attribute cannot exceed {label_max_length} characters")
    def label_length(self):
        return len(self.label) < self.label_max_length

    @JsonValidator(
        f"placeholder attribute cannot exceed {placeholder_max_length} characters"
    )
    def placeholder_length(self):
        return (
            self.placeholder is None
            or len(self.placeholder) < self.placeholder_max_length
        )

    @EnumValidator("data_source", DataSourceTypes)
    def data_source_valid(self):
        return self.data_source in self.DataSourceTypes

    def to_dict(self) -> dict:
        json = super().to_dict()
        if self.data_source == "external":
            if isinstance(self.value, Option):
                json["selected_options"] = extract_json([self.value], "dialog")
            elif self.value is not None:
                json["selected_options"] = Option.from_single_value(self.value)
        else:
            if isinstance(self.value, Option):
                json["value"] = self.value.value
            elif self.value is not None:
                json["value"] = self.value
        return json


class DialogStaticSelector(AbstractDialogSelector):
    """
    Use the select element for multiple choice selections allowing users to pick a
    single item from a list. True to web roots, this selection is displayed as a
    dropdown menu.

    https://api.slack.com/dialogs#select_elements
    """

    data_source = "static"

    options_max_length = 100

    def __init__(
        self,
        *,
        name: str,
        label: str,
        options: Union[List[Option], List[OptionGroup]],
        optional: bool = False,
        value: Union[Option, str] = None,
        placeholder: str = None,
    ):
        """
        Use the select element for multiple choice selections allowing users to pick
        a single item from a list. True to web roots, this selection is displayed as
        a dropdown menu.

        A select element may contain up to 100 selections, provided as a list of
        Option or OptionGroup objects

        https://api.slack.com/dialogs#attributes_select_elements

        Args:
            name: Name of form element. Required. No more than 300 characters.
            label: Label displayed to user. Required. No more than 48 characters.
            options: A list of up to 100 Option or OptionGroup objects. Object
                types cannot be mixed.
            optional: Provide true when the form element is not required. By
                default, form elements are required.
            value: Provide a default selected value.
            placeholder: A string displayed as needed to help guide users in
                completing the element. 150 character maximum.
        """
        super().__init__(
            name=name,
            label=label,
            optional=optional,
            value=value,
            placeholder=placeholder,
        )
        self.options = options

    @JsonValidator(f"options attribute cannot exceed {options_max_length} items")
    def options_length(self):
        return len(self.options) < self.options_max_length

    def to_dict(self) -> dict:
        json = super().to_dict()
        if isinstance(self.options[0], OptionGroup):
            json["option_groups"] = extract_json(self.options, "dialog")
        else:
            json["options"] = extract_json(self.options, "dialog")
        return json


class DialogUserSelector(AbstractDialogSelector):
    data_source = "users"

    def __init__(
        self,
        *,
        name: str,
        label: str,
        optional: bool = False,
        value: str = None,
        placeholder: str = None,
    ):
        """
        Now you can easily populate a select menu with a list of users. For example,
        when you are creating a bug tracking app, you want to include a field for an
        assignee. Slack pre-populates the user list in client-side, so your app
        doesn't need access to a related OAuth scope.

        https://api.slack.com/dialogs#dynamic_select_elements_users

        Args:
            name: Name of form element. Required. No more than 300 characters.
            label: Label displayed to user. Required. No more than 48 characters.
            optional: Provide true when the form element is not required. By
                default, form elements are required.
            value: Provide a default selected value.
            placeholder: A string displayed as needed to help guide users in
                completing the element. 150 character maximum.
        """
        super().__init__(
            name=name,
            label=label,
            optional=optional,
            value=value,
            placeholder=placeholder,
        )


class DialogChannelSelector(AbstractDialogSelector):
    data_source = "channels"

    def __init__(
        self,
        *,
        name: str,
        label: str,
        optional: bool = False,
        value: str = None,
        placeholder: str = None,
    ):
        """
        You can also provide a select menu with a list of channels. Specify your
        data_source as channels to limit only to public channels

        https://api.slack.com/dialogs#dynamic_select_elements_channels_conversations

        Args:
            name: Name of form element. Required. No more than 300 characters.
            label: Label displayed to user. Required. No more than 48 characters.
            optional: Provide true when the form element is not required. By
                default, form elements are required.
            value: Provide a default selected value.
            placeholder: A string displayed as needed to help guide users in
                completing the element. 150 character maximum.
        """
        super().__init__(
            name=name,
            label=label,
            optional=optional,
            value=value,
            placeholder=placeholder,
        )


class DialogConversationSelector(AbstractDialogSelector):
    data_source = "conversations"

    def __init__(
        self,
        *,
        name: str,
        label: str,
        optional: bool = False,
        value: str = None,
        placeholder: str = None,
    ):
        """
        You can also provide a select menu with a list of conversations - including
        private channels, direct messages, MPIMs, and whatever else we consider a
        conversation-like thing.

        https://api.slack.com/dialogs#dynamic_select_elements_channels_conversations

        Args:
            name: Name of form element. Required. No more than 300 characters.
            label: Label displayed to user. Required. No more than 48 characters.
            optional: Provide true when the form element is not required. By
                default, form elements are required.
            value: Provide a default selected value.
            placeholder: A string displayed as needed to help guide users in
                completing the element. 150 character maximum.
        """
        super().__init__(
            name=name,
            label=label,
            optional=optional,
            value=value,
            placeholder=placeholder,
        )


class DialogExternalSelector(AbstractDialogSelector):
    data_source = "external"

    @property
    def attributes(self) -> Set[str]:
        return super().attributes.union({"min_query_length"})

    def __init__(
        self,
        *,
        name: str,
        label: str,
        value: Optional[Option] = None,
        min_query_length: Optional[int] = None,
        optional: Optional[bool] = False,
        placeholder: str = None,
    ):
        """
        Use the select element for multiple choice selections allowing users to pick
        a single item from a list. True to web roots, this selection is displayed as
        a dropdown menu.

        A list of options can be loaded from an external URL and used in your dialog
        menus.

        https://api.slack.com/dialogs#dynamic_select_elements_external

        Args:
            name: Name of form element. Required. No more than 300 characters.
            label: Label displayed to user. Required. No more than 48 characters.
            min_query_length: Specify the number of characters that must be typed
                by a user into a dynamic select menu before dispatching to the app.
            optional: Provide true when the form element is not required. By
                default, form elements are required.
            value: Provide a default selected value. This should be a single
                Option or OptionGroup that exactly matches one that will be returned
                from your external endpoint.
            placeholder: A string displayed as needed to help guide users in
                completing the element. 150 character maximum.
        """
        super().__init__(
            name=name,
            label=label,
            value=value,
            optional=optional,
            placeholder=placeholder,
        )
        self.min_query_length = min_query_length
