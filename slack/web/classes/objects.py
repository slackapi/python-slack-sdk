from datetime import datetime
from functools import wraps
from typing import Callable, Iterable, List, NamedTuple, Set, Union

from ...errors import SlackObjectFormationError

ButtonStyles = {"primary", "danger"}
DynamicSelectElementTypes = {"users", "channels", "conversations"}


class JsonObject:
    @property
    def attributes(self) -> Set[str]:
        """
        Provide a set of attributes of this object that are part of its JSON structure
        """
        return set()

    def validate_json(self) -> None:
        """
        :raises SlackObjectFormationError if the object was not valid
        """
        for attribute in (func for func in dir(self) if not func.startswith("__")):
            method = getattr(self, attribute)
            if callable(method) and hasattr(method, "validator"):
                method()

    def get_non_null_keys(self) -> dict:
        """
        Construct a dictionary out of non-null keys present on this object
        """
        return {
            key: getattr(self, key, None)
            for key in sorted(self.attributes)
            if getattr(self, key, None) is not None
        }

    def get_json(self, *args) -> dict:
        """
        Return this object's Slack-valid JSON representation

        :param args: Any specific formatting args (rare; generally ignored)

        :return: a Python dict - (will be encoded later)

        :raises SlackObjectFormationError if the object was not valid
        """
        self.validate_json()
        return self.get_non_null_keys()

    def __str__(self):
        return f"<slack.{self.__class__.__name__}>"

    def __repr__(self):
        json = self.get_json()
        if json:
            return f"{json}"
        else:
            return self.__str__()


class JsonValidator:
    def __init__(self, message: str):
        """
        Decorate a method on a class to mark it as a JSON validator. Validation
        functions should return true if valid, false if not.

        :param message: Message to be attached to the thrown SlackObjectFormationError
        """
        self.message = message

    def __call__(self, func: Callable) -> Callable[..., None]:
        @wraps(func)
        def wrapped_f(*args, **kwargs):
            if not func(*args, **kwargs):
                raise SlackObjectFormationError(self.message)

        wrapped_f.validator = True
        return wrapped_f


class EnumValidator(JsonValidator):
    def __init__(self, attribute: str, enum: Iterable[str]):
        super().__init__(
            f"{attribute} attribute must be one of the following values: "
            f"{', '.join(enum)}"
        )


class IDNamePair(NamedTuple):
    """
    Simple type used to help with unpacking event data
    """

    id: str
    name: str


class Link(JsonObject):
    def __init__(self, *, url: str, text: str):
        """
        Base class used to generate links in Slack's not-quite Markdown, not quite HTML
        syntax

        https://api.slack.com/docs/message-formatting#linking_to_urls
        """
        self.url = url
        self.text = text

    def __str__(self):
        if self.text:
            separator = "|"
        else:
            separator = ""
        return f"<{self.url}{separator}{self.text}>"


class DateLink(Link):
    def __init__(
        self,
        *,
        date: Union[datetime, int],
        date_format: str,
        fallback: str,
        link: str = None,
    ):
        """
        Messages containing a date or time should be displayed in the local timezone
        of the person seeing the message. The <!date> command will format a Unix
        timestamp using tokens within a string that you set. You may also optionally
        link a date using a standard URL. A <!date> must include some fallback text
        for older Slack clients (in case the conversion fails).

        https://api.slack.com/docs/message-formatting#formatting_dates

        :param date: A Unix timestamp (as int) or datetime.datetime object

        :param date_format: Describe your date and time as a string, using any
            combination of the following tokens and plain text: {date_num}, {date},
            {date_short}, {date_long}, {date_pretty}, {date_short_pretty},
            {date_long_pretty}, {time}, {time_secs}

        :param fallback: text to display on clients that don't support date rendering

        :param link: an optional URL to hyperlink to with this date
        """
        if isinstance(date, datetime):
            epoch = int(date.timestamp())
        else:
            epoch = date
        if link is not None:
            link = f"^{link}"
        else:
            link = ""
        super().__init__(url=f"{epoch}^{date_format}{link}", text=fallback)


class ObjectLink(Link):
    prefix_mapping = {
        "C": "#",  # channel
        "G": "#",  # group message
        "U": "@",  # user
        "W": "@",  # workspace user (enterprise)
        "B": "@",  # bot user
        "S": "!subteam^",  # user groups, originally known as subteams
    }

    def __init__(self, *, object_id: str, text: str = ""):
        """
        Convenience class to create links to specific object types

        https://api.slack.com/docs/message-formatting#linking_to_channels_and_users

        :param object_id: An ID to create a link to, eg 'U12345' for a user,
            or 'C6789' for a channel

        :param text: Optional text to attach to the link - may or may not be
            displayed by Slack client
        """
        prefix = self.prefix_mapping.get(object_id[0].upper(), "@")
        super().__init__(url=f"{prefix}{object_id}", text=text)


class ChannelLink(Link):
    def __init__(self):
        """
        Represents an @channel link, which notifies everyone present in this channel.

        https://api.slack.com/docs/message-formatting#variables
        """
        super().__init__(url="!channel", text="channel")


class HereLink(Link):
    def __init__(self):
        """
        Represents an @here link, which notifies all online users of this channel.

        https://api.slack.com/docs/message-formatting#variables
        """
        super().__init__(url="!here", text="here")


class EveryoneLink(Link):
    def __init__(self):
        """
        Represents an @everyone link, which notifies all users of this workspace.

        https://api.slack.com/docs/message-formatting#variables
        """
        super().__init__(url="!everyone", text="everyone")


class TextObject(JsonObject):
    attributes = {"text", "type"}

    def __init__(self, *, text: str, type: str):
        """
        Super class for new text "objects" used in Block kit
        """
        self.text = text
        self.type = type


class PlainTextObject(TextObject):
    @property
    def attributes(self) -> Set[str]:
        return super().attributes.union({"emoji"})

    def __init__(self, *, text: str, emoji: bool = True):
        """
        A plain text object, meaning markdown characters will not be parsed as
        formatting information.

        https://api.slack.com/reference/messaging/composition-objects#text

        :param emoji: Whether to escape emoji in text into Slack's :emoji: format
        """
        super().__init__(text=text, type="plain_text")
        self.emoji = emoji

    @staticmethod
    def from_string(text: str) -> dict:
        """
        Transforms a string into the required object shape to act as a PlainTextObject
        """
        return PlainTextObject(text=text).get_json()


class MarkdownTextObject(TextObject):
    @property
    def attributes(self) -> Set[str]:
        return super().attributes.union({"verbatim"})

    def __init__(self, *, text: str, verbatim: bool = False):
        """
        A Markdown text object, meaning markdown characters will be parsed as
        formatting information.

        https://api.slack.com/reference/messaging/composition-objects#text

        :param verbatim: When set to false (as is default) URLs will be
            auto-converted into links, conversation names will be link-ified, and
            certain mentions will be automatically parsed.
        """
        super().__init__(text=text, type="mrkdwn")
        self.verbatim = verbatim

    @staticmethod
    def from_string(text: str) -> dict:
        """
        Transforms a string into the required object shape to act as a
        MarkdownTextObject
        """
        return MarkdownTextObject(text=text).get_json()

    @staticmethod
    def from_link(link: Link, title: str = "") -> dict:
        """
        Transform a Link object directly into the required object shape to act as a
        MarkdownTextObject
        """
        if title:
            title = f": {title}"
        return MarkdownTextObject(text=f"{link}{title}").get_json()


class ConfirmObject(JsonObject):
    def __init__(
        self,
        *,
        title: str,
        text: Union[TextObject, str],
        confirm: str = "Yes",
        deny: str = "No",
    ):
        """
        An object that defines a dialog that provides a confirmation step to any
        interactive element. This dialog will ask the user to confirm their action by
        offering a confirm and deny button.

        https://api.slack.com/reference/messaging/composition-objects#confirm

        :param title: A string that defines the dialog's title. Cannot exceed 100
            characters.

        :param text: A string or TextObject that defines the explanatory text
            that appears in the confirm dialog. Cannot exceed 300 characters.

        :param confirm: A string to define the text on the button that confirms the
            action. Cannot exceed 30 characters.

        :param deny: A string to define the text on the button that cancels the
            action. Cannot exceed 30 characters.
        """
        self.title = title
        self.text = text
        self.confirm = confirm
        self.deny = deny

    @JsonValidator("title attribute cannot exceed 100 characters")
    def title_length(self):
        return len(self.title) <= 100

    @JsonValidator("text attribute cannot exceed 300 characters")
    def text_length(self):
        if isinstance(self.text, TextObject):
            return len(self.text.text) <= 300
        else:
            return len(self.text) <= 300

    @JsonValidator("confirm attribute cannot exceed 30 characters")
    def confirm_length(self):
        return len(self.confirm) <= 30

    @JsonValidator("deny attribute cannot exceed 30 characters")
    def deny_length(self):
        return len(self.deny) <= 30

    def get_json(self, option_type: str = "block") -> dict:
        if option_type == "action":
            # deliberately skipping JSON validators here - can't find documentation
            # on actual limits here
            return {
                "text": self.text,
                "title": self.title,
                "ok_text": self.confirm if self.confirm != "Yes" else "Okay",
                "dismiss_text": self.deny if self.deny != "No" else "Cancel",
            }
        else:
            self.validate_json()
            json = {
                "title": PlainTextObject.from_string(self.title),
                "confirm": PlainTextObject.from_string(self.confirm),
                "deny": PlainTextObject.from_string(self.deny),
            }
            if isinstance(self.text, TextObject):
                json["text"] = self.text.get_json()
            else:
                json["text"] = MarkdownTextObject.from_string(self.text)
            return json


class OptionObject(JsonObject):
    """
    Option object used in dialogs, legacy message actions, and blocks

    JSON must be retrieved with an explicit option_type - the Slack API has
    different required formats in different situations
    """

    def __init__(self, *, label: str, value: str, description: str = None):
        """
        An object that represents a single selectable item in a block element (
        SelectElement, OverflowMenuElement) or dialog element
        (StaticDialogSelectElement)

        Blocks:
        https://api.slack.com/reference/messaging/composition-objects#option

        Dialogs:
        https://api.slack.com/dialogs#select_elements

        Legacy interactive attachments:
        https://api.slack.com/docs/interactive-message-field-guide#option_fields

        :param label: A short, user-facing string to label this option to users.
            Cannot exceed 75 characters.

        :param value: A short string that identifies this particular option to your
            application. It will be part of the payload when this option is selected.
            Cannot exceed 75 characters.

        :param description: A user-facing string that provides more details about
            this option. Only supported in legacy message actions, not in blocks or
            dialogs.
        """
        self.label = label
        self.value = value
        self.description = description

    @JsonValidator("label attribute cannot exceed 75 characters")
    def label_length(self):
        return len(self.label) <= 75

    @JsonValidator("value attribute cannot exceed 75 characters")
    def value_length(self):
        return len(self.value) <= 75

    def get_json(self, option_type: str = "block") -> dict:
        """
        Different parent classes must call this with a valid value from OptionTypes -
        either "dialog", "action", or "block", so that JSON is returned in the
        correct shape.
        """
        self.validate_json()
        if option_type == "dialog":
            return {"label": self.label, "value": self.value}
        elif option_type == "action":
            json = {"text": self.label, "value": self.value}
            if self.description is not None:
                json["description"] = self.description
            return json
        else:  # if option_type == "block"; this should be the most common case
            return {
                "text": PlainTextObject.from_string(self.label),
                "value": self.value,
            }

    @staticmethod
    def from_single_value(value_and_label: str):
        """
        Creates a simple Option instance with the same value and label
        """
        return OptionObject(value=value_and_label, label=value_and_label)


class OptionGroupObject(JsonObject):
    """
    JSON must be retrieved with an explicit option_type - the Slack API has
    different required formats in different situations
    """

    def __init__(self, *, label: str, options: List[OptionObject]):
        """
        Create a group of Option objects - pass in a label (that will be part of the
        UI) and a list of Option objects.

        Blocks:
        https://api.slack.com/reference/messaging/composition-objects#option-group

        Dialogs:
        https://api.slack.com/dialogs#select_elements

        Legacy interactive attachments:
        https://api.slack.com/docs/interactive-message-field-guide#option_groups_to_place_within_message_menu_actions

        :param label: Text to display at the top of this group of options.

        :param options: A list of no more than 100 Option objects.
        """  # noqa prevent flake8 blowing up on the long URL
        self.label = label
        self.options = options

    @JsonValidator("label attribute cannot exceed 75 characters")
    def label_length(self):
        return len(self.label) <= 75

    @JsonValidator("options attribute cannot exceed 100 elements")
    def options_length(self):
        return len(self.options) <= 100

    def get_json(self, option_type: str = "block") -> dict:
        self.validate_json()
        if option_type == "dialog":
            return {
                "label": self.label,
                "options": extract_json(self.options, OptionObject, option_type),
            }
        elif option_type == "action":
            return {
                "text": self.label,
                "options": extract_json(self.options, OptionObject, option_type),
            }
        else:  # if option_type == "block"; this should be the most common case
            return {
                "label": PlainTextObject.from_string(self.label),
                "options": extract_json(self.options, OptionObject, option_type),
            }


OptionTypes = (OptionObject, OptionGroupObject)


def extract_json(
    item_or_items: Union[JsonObject, List[JsonObject], str],
    expected_object: type(JsonObject),
    *format_args,
) -> Union[dict, List[dict], str]:
    """
    Given a sequence (or single item), attempt to call the get_json() method on each
    item and return a plain list. If item is not the expected type, return it
    unmodified, in case it's already a plain dict or some other user created class.

    :param item_or_items: item(s) to go through

    :param expected_object: a subclass of JsonObject that's expected in this attribute

    :param format_args: Any formatting specifiers to pass into the object's get_json
    method
    """
    try:
        return [
            elem.get_json(*format_args) if isinstance(elem, expected_object) else elem
            for elem in item_or_items
        ]
    except TypeError:  # not iterable, so try returning it as a single item
        return (
            item_or_items.get_json(*format_args)
            if isinstance(item_or_items, expected_object)
            else item_or_items
        )
