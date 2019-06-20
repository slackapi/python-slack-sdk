from abc import ABCMeta, abstractmethod
from typing import List, Set, Union

from .objects import (
    ButtonStyles,
    ConfirmObject,
    DynamicSelectElementTypes,
    EnumValidator,
    JsonObject,
    JsonValidator,
    Option,
    OptionGroup,
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

    @JsonValidator("name or url attribute is required")
    def name_or_url_present(self):
        return self.name is not None or self.url is not None


class ActionButton(Action):
    @property
    def attributes(self):
        return super().attributes.union({"value", "style"})

    value_max_length = 2000

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

        Args:
            name: Name this specific action. The name will be returned to your
                Action URL along with the message's callback_id when this action is
                invoked. Use it to identify this particular response path.
            text: The user-facing label for the message button or menu
                representing this action. Cannot contain markup.
            value: Provide a string identifying this specific action. It will be
                sent to your Action URL along with the name and attachment's
                callback_id . If providing multiple actions with the same name, value
                can be strategically used to differentiate intent. Cannot exceed 2000
                characters.
            confirm: a ConfirmObject that will appear in a dialog to confirm
                user's choice.
            style: Leave blank to indicate that this is an ordinary button. Use
                "primary" or "danger" to mark important buttons.
        """
        super().__init__(name=name, text=text, type="button")
        self.value = value
        self.confirm = confirm
        self.style = style

    @JsonValidator(f"value attribute cannot exceed {value_max_length} characters")
    def value_length(self):
        return len(self.value) <= self.value_max_length

    @EnumValidator("style", ButtonStyles)
    def style_valid(self):
        return self.style is None or self.style in ButtonStyles

    def get_json(self) -> dict:
        json = super().get_json()
        if self.confirm is not None:
            json["confirm"] = extract_json(self.confirm, "action")
        return json


class ActionLinkButton(Action):
    def __init__(self, *, text: str, url: str):
        """
        A simple interactive button that just opens a URL

        https://api.slack.com/docs/message-attachments#link_buttons

        Args:
          text: text to display on the button, eg 'Click Me!"
          url: the URL to open
        """
        super().__init__(text=text, url=url, type="button")


class AbstractActionSelector(Action, metaclass=ABCMeta):
    DataSourceTypes = DynamicSelectElementTypes.union({"external", "static"})

    attributes = {"name", "text", "type", "data_source"}

    @property
    @abstractmethod
    def data_source(self) -> str:
        pass

    def __init__(self, *, name: str, text: str, selected_option: Option = None):
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
            json["selected_options"] = extract_json([self.selected_option], "action")
        return json


class ActionStaticSelector(AbstractActionSelector):
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
        text: str,
        options: List[Union[Option, OptionGroup]],
        selected_option: Option = None,
    ):
        """
        Help users make clear, concise decisions by providing a menu of options
        within messages.

        https://api.slack.com/docs/message-menus

        Args:
            name: Name this specific action. The name will be returned to your
                Action URL along with the message's callback_id when this action is
                invoked. Use it to identify this particular response path.
            text: The user-facing label for the message button or menu
                representing this action. Cannot contain markup.
            options: A list of no mre than 100 Option or OptionGroup objects
            selected_option: An Option object to pre-select as the default
                value.
        """
        super().__init__(name=name, text=text, selected_option=selected_option)
        self.options = options

    @JsonValidator(f"options attribute cannot exceed {options_max_length} items")
    def options_length(self):
        return len(self.options) < self.options_max_length

    def get_json(self) -> dict:
        json = super().get_json()
        if isinstance(self.options[0], OptionGroup):
            json["option_groups"] = extract_json(self.options, "action")
        else:
            json["options"] = extract_json(self.options, "action")
        return json


class ActionUserSelector(AbstractActionSelector):
    data_source = "users"

    def __init__(self, name: str, text: str, selected_user: Option = None):
        """
        Automatically populate the selector with a list of users in the workspace.

        https://api.slack.com/docs/message-menus#allow_users_to_select_from_a_list_of_members

        Args:
            name: Name this specific action. The name will be returned to your
                Action URL along with the message's callback_id when this action is
                invoked. Use it to identify this particular response path.
            text: The user-facing label for the message button or menu
                representing this action. Cannot contain markup.
            selected_user: An Option object to pre-select as the default
                value.
        """
        super().__init__(name=name, text=text, selected_option=selected_user)


class ActionChannelSelector(AbstractActionSelector):
    data_source = "channels"

    def __init__(self, name: str, text: str, selected_channel: Option = None):
        """
        Automatically populate the selector with a list of public channels in the
        workspace.

        https://api.slack.com/docs/message-menus#let_users_choose_one_of_their_workspace_s_channels

        Args:
            name: Name this specific action. The name will be returned to your
                Action URL along with the message's callback_id when this action is
                invoked. Use it to identify this particular response path.
            text: The user-facing label for the message button or menu
                representing this action. Cannot contain markup.
            selected_channel: An Option object to pre-select as the default
                value.
        """
        super().__init__(name=name, text=text, selected_option=selected_channel)


class ActionConversationSelector(AbstractActionSelector):
    data_source = "conversations"

    def __init__(self, name: str, text: str, selected_conversation: Option = None):
        """
        Automatically populate the selector with a list of conversations they have in
        the workspace.

        https://api.slack.com/docs/message-menus#let_users_choose_one_of_their_conversations

        Args:
            name: Name this specific action. The name will be returned to your
                Action URL along with the message's callback_id when this action is
                invoked. Use it to identify this particular response path.
            text: The user-facing label for the message button or menu
                representing this action. Cannot contain markup.
            selected_conversation: An Option object to pre-select as the default
                value.
        """
        super().__init__(name=name, text=text, selected_option=selected_conversation)


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
        selected_option: Option = None,
        min_query_length: int = None,
    ):
        """
        Populate a message select menu from your own application dynamically.

        https://api.slack.com/docs/message-menus#populate_message_menus_dynamically

        Args:
            name: Name this specific action. The name will be returned to your
                Action URL along with the message's callback_id when this action is
                invoked. Use it to identify this particular response path.
            text: The user-facing label for the message button or menu
                representing this action. Cannot contain markup.
            selected_option: An Option object to pre-select as the default
                value.
            min_query_length: Specify the number of characters that must be typed
                by a user into a dynamic select menu before dispatching to the app.
        """
        super().__init__(name=name, text=text, selected_option=selected_option)
        self.min_query_length = min_query_length
