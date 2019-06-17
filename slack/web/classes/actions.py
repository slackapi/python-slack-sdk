from abc import ABCMeta, abstractmethod
from typing import List, Set, Union

from .objects import (
    ButtonStyles,
    ConfirmObject,
    DynamicSelectElementTypes,
    EnumValidator,
    JsonObject,
    JsonValidator,
    OptionGroupObject,
    OptionObject,
    OptionTypes,
    extract_json,
)


class Action(JsonObject):
    """
    https://api.slack.com/docs/message-attachments#action_fields

    https://api.slack.com/docs/interactive-message-field-guide#message_action_fields
    """

    attributes = {"name", "text", "type", "url"}

    def __init__(self, *, text: str, type: str, name: str = None, url: str = None):
        self.name = name
        self.url = url
        self.text = text
        self.type = type

    @JsonValidator("name attribute is required")
    def name_or_url_present(self):
        return self.name is not None or self.url is not None


class ActionButton(Action):
    @property
    def attributes(self):
        return super().attributes.union({"value", "style"})

    def __init__(
        self,
        *,
        name: str,
        text: str,
        value: str,
        confirm: ConfirmObject = None,
        style: str = None,
    ):
        """
        Simple button for use inside attachments

        https://api.slack.com/docs/message-buttons

        :param name: Name this specific action. The name will be returned to your
            Action URL along with the message's callback_id when this action is invoked.
            Use it to identify this particular response path.

        :param text: The user-facing label for the message button or menu
            representing this action. Cannot contain markup.

        :param value: Provide a string identifying this specific action. It will be
            sent to your Action URL along with the name and attachment's callback_id. If
            providing multiple actions with the same name, value can be strategically
            used to differentiate intent. Cannot exceed 2000 characters.

        :param confirm: a ConfirmObject that will appear in a dialog to confirm
            user's choice.

        :param style: Leave blank to indicate that this is an ordinary button. Use
            "primary" or "danger" to mark important buttons.
        """
        super().__init__(name=name, text=text, type="button")
        self.value = value
        self.confirm = confirm
        self.style = style

    @JsonValidator("value attribute cannot exceed 2000 characters")
    def value_length(self):
        return len(self.value) <= 2000

    @EnumValidator("style", ButtonStyles)
    def style_valid(self):
        return self.style is None or self.style in ButtonStyles

    def get_json(self) -> dict:
        json = super().get_json()
        if self.confirm is not None:
            json["confirm"] = extract_json(self.confirm, ConfirmObject, "action")
        return json


class ActionLinkButton(Action):
    def __init__(self, *, text: str, url: str):
        """
        A simple interactive button that just opens a URL

        https://api.slack.com/docs/message-attachments#link_buttons

        :param text: text to display on the button, eg 'Click Me!"

        :param url: the URL to open
        """
        super().__init__(text=text, url=url, type="button")


class AbstractActionSelector(Action, metaclass=ABCMeta):
    DataSourceTypes = DynamicSelectElementTypes.union({"external", "static"})

    attributes = {"name", "text", "type", "data_source"}

    @property
    @abstractmethod
    def data_source(self) -> str:
        pass

    def __init__(self, *, name: str, text: str, selected_option: OptionObject = None):
        super().__init__(text=text, name=name, type="select")
        self.selected_option = selected_option

    @EnumValidator("data_source", DataSourceTypes)
    def data_source_valid(self):
        return self.data_source in self.DataSourceTypes

    def get_json(self, *args) -> dict:
        json = super().get_json()
        if self.selected_option is not None:
            # this is a special case for ExternalActionSelectElement - in that case,
            # you pass the initial value of the selector as a selected_options array
            json["selected_options"] = extract_json(
                [self.selected_option], OptionTypes, "action"
            )
        return json


class ActionStaticSelector(AbstractActionSelector):
    """
    Use the select element for multiple choice selections allowing users to pick a
    single item from a list. True to web roots, this selection is displayed as a
    dropdown menu.

    https://api.slack.com/dialogs#select_elements
    """

    data_source = "static"

    def __init__(
        self,
        *,
        name: str,
        text: str,
        options: List[Union[OptionObject, OptionGroupObject]],
        selected_option: OptionObject = None,
    ):
        """
        Help users make clear, concise decisions by providing a menu of options
        within messages.

        https://api.slack.com/docs/message-menus

        :param name: Name this specific action. The name will be returned to your
            Action URL along with the message's callback_id when this action is invoked.
            Use it to identify this particular response path.

        :param text: The user-facing label for the message button or menu
            representing this action. Cannot contain markup.

        :param options: A list of no mre than 100 Option or OptionGroup objects

        :param selected_option: An OptionObject object to pre-select as the default
            value.
        """
        super().__init__(name=name, text=text, selected_option=selected_option)
        self.options = options

    @JsonValidator("options attribute cannot exceed 100 items")
    def options_length(self):
        return len(self.options) < 100

    @JsonValidator(
        "options attribute cannot contain mixed OptionGroup and Option items"
    )
    def options_valid(self):
        return all(isinstance(o, OptionObject) for o in self.options) or all(
            isinstance(o, OptionGroupObject) for o in self.options
        )

    def get_json(self) -> dict:
        json = super().get_json()
        if isinstance(self.options[0], OptionObject):
            json["options"] = extract_json(self.options, OptionTypes, "action")
        else:
            json["option_groups"] = extract_json(self.options, OptionTypes, "action")
        return json


class ActionUserSelector(AbstractActionSelector):
    data_source = "users"

    def __init__(self, name: str, text: str, selected_option: OptionObject = None):
        """
        Automatically populate the selector with a list of users in the workspace.

        https://api.slack.com/docs/message-menus#allow_users_to_select_from_a_list_of_members

        :param name: Name this specific action. The name will be returned to your
            Action URL along with the message's callback_id when this action is invoked.
            Use it to identify this particular response path.

        :param text: The user-facing label for the message button or menu
            representing this action. Cannot contain markup.

        :param selected_option: An OptionObject object to pre-select as the default
            value.
        """
        super().__init__(name=name, text=text, selected_option=selected_option)


class ActionChannelSelector(AbstractActionSelector):
    data_source = "channels"

    def __init__(self, name: str, text: str, selected_option: OptionObject = None):
        """
        Automatically populate the selector with a list of public channels in the
        workspace.

        https://api.slack.com/docs/message-menus#let_users_choose_one_of_their_workspace_s_channels

        :param name: Name this specific action. The name will be returned to your
            Action URL along with the message's callback_id when this action is invoked.
            Use it to identify this particular response path.

        :param text: The user-facing label for the message button or menu
            representing this action. Cannot contain markup.

        :param selected_option: An OptionObject object to pre-select as the default
            value.
        """
        super().__init__(name=name, text=text, selected_option=selected_option)


class ActionConversationSelector(AbstractActionSelector):
    data_source = "conversations"

    def __init__(self, name: str, text: str, selected_option: OptionObject = None):
        """
        Automatically populate the selector with a list of conversations they have in
        the workspace.

        https://api.slack.com/docs/message-menus#let_users_choose_one_of_their_conversations

        :param name: Name this specific action. The name will be returned to your
            Action URL along with the message's callback_id when this action is invoked.
            Use it to identify this particular response path.

        :param text: The user-facing label for the message button or menu
            representing this action. Cannot contain markup.

        :param selected_option: An OptionObject object to pre-select as the default
            value.
        """
        super().__init__(name=name, text=text, selected_option=selected_option)


class ActionExternalSelector(AbstractActionSelector):
    data_source = "external"

    @property
    def attributes(self) -> Set[str]:
        return super().attributes.union({"min_query_length"})

    def __init__(
        self,
        *,
        name: str,
        text: str,
        selected_option: OptionObject = None,
        min_query_length: int = None,
    ):
        """
        Populate a message select menu from your own application dynamically.

        https://api.slack.com/docs/message-menus#populate_message_menus_dynamically

        :param name: Name this specific action. The name will be returned to your
            Action URL along with the message's callback_id when this action is invoked.
            Use it to identify this particular response path.

        :param text: The user-facing label for the message button or menu
            representing this action. Cannot contain markup.

        :param selected_option: An OptionObject object to pre-select as the default
            value.

        :param min_query_length: Specify the number of characters that must be typed
            by a user into a dynamic select menu before dispatching to the app.
        """
        super().__init__(name=name, text=text, selected_option=selected_option)
        self.min_query_length = min_query_length
