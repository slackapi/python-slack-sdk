from json import dumps
from typing import List, Optional, Union

from . import JsonObject, JsonValidator, extract_json
from .dialog_elements import (
    AbstractDialogSelector,
    DialogChannelSelector,
    DialogConversationSelector,
    DialogExternalSelector,
    DialogStaticSelector,
    DialogTextArea,
    DialogTextComponent,
    DialogTextField,
    DialogUserSelector,
)
from .objects import Option, OptionGroup


class DialogBuilder(JsonObject):
    attributes = {}  # no attributes because to_dict has unique implementation

    _callback_id: Optional[str]
    _elements: List[Union[DialogTextComponent, AbstractDialogSelector]]
    _submit_label: Optional[str]
    _notify_on_cancel: bool
    _state: Optional[str]

    title_max_length = 24
    submit_label_max_length = 24
    elements_max_length = 10
    state_max_length = 3000

    def __init__(self):
        """
        Create a DialogBuilder to more easily construct the JSON required to submit a
        dialog to Slack
        """
        self._title = None
        self._callback_id = None
        self._elements = []
        self._submit_label = None
        self._notify_on_cancel = False
        self._state = None

    def title(self, title: str) -> "DialogBuilder":
        """
        Specify a title for this dialog

        Args:
          title: must not exceed 24 characters
        """
        self._title = title
        return self

    def state(self, state: Union[dict, str]) -> "DialogBuilder":
        """
        Pass state into this dialog - dictionaries will be automatically formatted to
        JSON

        Args:
            state: Extra state information that you need to pass from this dialog
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

        Args:
          callback_id: a string identifying this particular dialog
        """
        self._callback_id = callback_id
        return self

    def submit_label(self, label: str) -> "DialogBuilder":
        """
        The label to use on the 'Submit' button on the dialog. Defaults to 'Submit'
        if not specified.

        Args:
            label: must not exceed 24 characters, and must be a single word (no
                spaces)
        """
        self._submit_label = label
        return self

    def notify_on_cancel(self, notify: bool) -> "DialogBuilder":
        """
        Whether this dialog should send a request to your application even if the
        user cancels their interaction. Defaults to False.

        Args:
            notify: Set to True to indicate that your application should receive a
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
        placeholder: Optional[str] = None,
        hint: Optional[str] = None,
        value: Optional[str] = None,
        min_length: int = 0,
        max_length: int = 150,
        subtype: Optional[str] = None,
    ) -> "DialogBuilder":
        """
        Text elements are single-line plain text fields.

        https://api.slack.com/dialogs#attributes_text_elements

        Args:
            name: Name of form element. Required. No more than 300 characters.
            label: Label displayed to user. Required. 48 character maximum.
            optional: Provide true when the form element is not required. By
                default, form elements are required.
            placeholder: A string displayed as needed to help guide users in
                completing the element. 150 character maximum.
            hint: Helpful text provided to assist users in answering a question.
                Up to 150 characters.
            value: A default value for this field. Up to 150 characters.
            min_length: Minimum input length allowed for element. Up to 150
                characters. Defaults to 0.
            max_length: Maximum input length allowed for element. Up to 150
                characters. Defaults to 150.
            subtype: A subtype for this text input. Accepts email, number, tel,
                    or url. In some form factors, optimized input is provided for this
                    subtype.
        """
        self._elements.append(
            DialogTextField(
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
        placeholder: Optional[str] = None,
        hint: Optional[str] = None,
        value: Optional[str] = None,
        min_length: int = 0,
        max_length: int = 3000,
        subtype: Optional[str] = None,
    ) -> "DialogBuilder":
        """
        A textarea is a multi-line plain text editing control. You've likely
        encountered these on the world wide web. Use this element if you want a
        relatively long answer from users. The element UI provides a remaining
        character count to the max_length you have set or the default,
        3000.

        https://api.slack.com/dialogs#attributes_textarea_elements

        Args:
            name: Name of form element. Required. No more than 300 characters.
            label: Label displayed to user. Required. 48 character maximum.
            optional: Provide true when the form element is not required. By
                default, form elements are required.
            placeholder: A string displayed as needed to help guide users in
                completing the element. 150 character maximum.
            hint: Helpful text provided to assist users in answering a question.
                Up to 150 characters.
            value: A default value for this field. Up to 3000 characters.
            min_length: Minimum input length allowed for element. 1-3000
                characters. Defaults to 0.
            max_length: Maximum input length allowed for element. 0-3000
                characters. Defaults to 3000.
            subtype: A subtype for this text input. Accepts email, number, tel,
                or url. In some form factors, optimized input is provided for this
                subtype.
        """
        self._elements.append(
            DialogTextArea(
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

    def static_selector(
        self,
        *,
        name: str,
        label: str,
        options: Union[List[Option], List[OptionGroup]],
        optional: bool = False,
        value: Optional[str] = None,
        placeholder: Optional[str] = None,
    ) -> "DialogBuilder":
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
        self._elements.append(
            DialogStaticSelector(
                name=name,
                label=label,
                options=options,
                optional=optional,
                value=value,
                placeholder=placeholder,
            )
        )
        return self

    def external_selector(
        self,
        *,
        name: str,
        label: str,
        optional: bool = False,
        value: Optional[Option] = None,
        placeholder: Optional[str] = None,
        min_query_length: Optional[int] = None,
    ) -> "DialogBuilder":
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
            min_query_length: Specify the number of characters that must be
                typed by a user into a dynamic select menu before dispatching to your
                application.
            optional: Provide true when the form element is not required. By
                default, form elements are required.
            value: Provide a default selected value. This should be a single
                Option or OptionGroup that exactly matches one that will be returned
                from your external endpoint.
            placeholder: A string displayed as needed to help guide users in
                completing the element. 150 character maximum.
        """
        self._elements.append(
            DialogExternalSelector(
                name=name,
                label=label,
                optional=optional,
                value=value,
                placeholder=placeholder,
                min_query_length=min_query_length,
            )
        )
        return self

    def user_selector(
        self,
        *,
        name: str,
        label: str,
        optional: bool = False,
        value: Optional[str] = None,
        placeholder: Optional[str] = None,
    ) -> "DialogBuilder":
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
        self._elements.append(
            DialogUserSelector(
                name=name,
                label=label,
                optional=optional,
                value=value,
                placeholder=placeholder,
            )
        )
        return self

    def channel_selector(
        self,
        *,
        name: str,
        label: str,
        optional: bool = False,
        value: Optional[str] = None,
        placeholder: Optional[str] = None,
    ) -> "DialogBuilder":
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
        self._elements.append(
            DialogChannelSelector(
                name=name,
                label=label,
                optional=optional,
                value=value,
                placeholder=placeholder,
            )
        )
        return self

    def conversation_selector(
        self,
        *,
        name: str,
        label: str,
        optional: bool = False,
        value: Optional[str] = None,
        placeholder: Optional[str] = None,
    ) -> "DialogBuilder":
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
        self._elements.append(
            DialogConversationSelector(
                name=name,
                label=label,
                optional=optional,
                value=value,
                placeholder=placeholder,
            )
        )
        return self

    @JsonValidator("title attribute is required")
    def title_present(self):
        return self._title is not None

    @JsonValidator(f"title attribute cannot exceed {title_max_length} characters")
    def title_length(self):
        return self._title is not None and len(self._title) <= self.title_max_length

    @JsonValidator("callback_id attribute is required")
    def callback_id_present(self):
        return self._callback_id is not None

    @JsonValidator(f"dialogs must contain between 1 and {elements_max_length} elements")
    def elements_length(self):
        return 0 < len(self._elements) <= self.elements_max_length

    @JsonValidator(f"submit_label cannot exceed {submit_label_max_length} characters")
    def submit_label_length(self):
        return (
            self._submit_label is None
            or len(self._submit_label) <= self.submit_label_max_length
        )

    @JsonValidator("submit_label can only be one word")
    def submit_label_valid(self):
        return self._submit_label is None or " " not in self._submit_label

    @JsonValidator(f"state cannot exceed {state_max_length} characters")
    def state_length(self):
        return not self._state or len(self._state) <= self.state_max_length

    def to_dict(self) -> dict:  # skipcq: PYL-W0221
        self.validate_json()
        json = {
            "title": self._title,
            "callback_id": self._callback_id,
            "elements": extract_json(self._elements),
            "notify_on_cancel": self._notify_on_cancel,
        }
        if self._submit_label is not None:
            json["submit_label"] = self._submit_label
        if self._state is not None:
            json["state"] = self._state
        return json
