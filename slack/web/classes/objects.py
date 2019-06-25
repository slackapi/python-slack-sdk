from datetime import datetime
from typing import List, Optional, Set, Union

from . import BaseObject, JsonObject, JsonValidator, extract_json

ButtonStyles = {"danger", "primary"}
DynamicSelectElementTypes = {"channels", "conversations", "users"}


class Link(BaseObject):
    def __init__(self, *, url: str, text: str):
        """
        Base class used to generate links in Slack's not-quite Markdown, not quite HTML
        syntax

        https://api.slack.com/docs/message-formatting#linking_to_urls

        Args:
            url: The URL (or other special text, see subclasses) to link to
            text: Text to display on the link. Often only a fallback.
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
        link: Optional[str] = None,
    ):
        """
        Messages containing a date or time should be displayed in the local timezone
        of the person seeing the message. The <!date> command will format a Unix
        timestamp using tokens within a string that you set. You may also optionally
        link a date using a standard URL. A <!date> must include some fallback text
        for older Slack clients (in case the conversion fails).

        https://api.slack.com/docs/message-formatting#formatting_dates

        Args:
            date: A Unix timestamp (as int) or datetime.datetime object
            date_format: Describe your date and time as a string, using any
                combination of the following tokens and plain text: {date_num}, {date},
                {date_short}, {date_long}, {date_pretty}, {date_short_pretty},
                {date_long_pretty}, {time}, {time_secs}
            fallback: text to display on clients that don't support date rendering
            link: an optional URL to hyperlink to with this date
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

        Args:
            object_id: An ID to create a link to, eg 'U12345' for a user,
                or 'C6789' for a channel
            text: Optional text to attach to the link - may or may not be
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

    def __init__(self, *, text: str, subtype: str):
        """
        Super class for new text "objects" used in Block kit
        """
        self.text = text
        self.subtype = subtype

    def to_dict(self) -> dict:
        json = super().to_dict()
        json["type"] = self.subtype
        return json


class PlainTextObject(TextObject):
    @property
    def attributes(self) -> Set[str]:
        return super().attributes.union({"emoji"})

    def __init__(self, *, text: str, emoji: bool = True):
        """
        A plain text object, meaning markdown characters will not be parsed as
        formatting information.

        https://api.slack.com/reference/messaging/composition-objects#text

        Args:
            emoji: Whether to escape emoji in text into Slack's :emoji: format
        """
        super().__init__(text=text, subtype="plain_text")
        self.emoji = emoji

    @staticmethod
    def direct_from_string(text: str) -> dict:
        """
        Transforms a string into the required object shape to act as a PlainTextObject
        """
        return PlainTextObject(text=text).to_dict()


class MarkdownTextObject(TextObject):
    @property
    def attributes(self) -> Set[str]:
        return super().attributes.union({"verbatim"})

    def __init__(self, *, text: str, verbatim: bool = False):
        """
        A Markdown text object, meaning markdown characters will be parsed as
        formatting information.

        https://api.slack.com/reference/messaging/composition-objects#text

        Args:
            verbatim: When set to false (as is default) URLs will be
                auto-converted into links, conversation names will be link-ified, and
                certain mentions will be automatically parsed.
        """
        super().__init__(text=text, subtype="mrkdwn")
        self.verbatim = verbatim

    @staticmethod
    def direct_from_string(text: str) -> dict:
        """
        Transforms a string into the required object shape to act as a
        MarkdownTextObject
        """
        return MarkdownTextObject(text=text).to_dict()

    @staticmethod
    def direct_from_link(link: Link, title: str = "") -> dict:
        """
        Transform a Link object directly into the required object shape to act as a
        MarkdownTextObject
        """
        if title:
            title = f": {title}"
        return MarkdownTextObject(text=f"{link}{title}").to_dict()


class ConfirmObject(JsonObject):
    attributes = {}  # no attributes because to_dict has unique implementations

    title_max_length = 100
    text_max_length = 300
    confirm_max_length = 30
    deny_max_length = 30

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

        Args:
            title: A string that defines the dialog's title. Cannot exceed 100
                characters.
            text: A string or TextObject that defines the explanatory text
                that appears in the confirm dialog. Cannot exceed 300 characters.
            confirm: A string to define the text on the button that confirms the
                action. Cannot exceed 30 characters.
            deny: A string to define the text on the button that cancels the
                action. Cannot exceed 30 characters.
        """
        self.title = title
        self.text = text
        self.confirm = confirm
        self.deny = deny

    @JsonValidator(f"title attribute cannot exceed {title_max_length} characters")
    def title_length(self):
        return len(self.title) <= self.title_max_length

    @JsonValidator(f"text attribute cannot exceed {text_max_length} characters")
    def text_length(self):
        if isinstance(self.text, TextObject):
            return len(self.text.text) <= self.text_max_length
        else:
            return len(self.text) <= self.text_max_length

    @JsonValidator(f"confirm attribute cannot exceed {confirm_max_length} characters")
    def confirm_length(self):
        return len(self.confirm) <= self.confirm_max_length

    @JsonValidator(f"deny attribute cannot exceed {deny_max_length} characters")
    def deny_length(self):
        return len(self.deny) <= self.deny_max_length

    def to_dict(self, option_type: str = "block") -> dict:
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
                "title": PlainTextObject.direct_from_string(self.title),
                "confirm": PlainTextObject.direct_from_string(self.confirm),
                "deny": PlainTextObject.direct_from_string(self.deny),
            }
            if isinstance(self.text, TextObject):
                json["text"] = self.text.to_dict()
            else:
                json["text"] = MarkdownTextObject.direct_from_string(self.text)
            return json


class Option(JsonObject):
    """
    Option object used in dialogs, legacy message actions, and blocks

    JSON must be retrieved with an explicit option_type - the Slack API has
    different required formats in different situations
    """

    attributes = {}  # no attributes because to_dict has unique implementations

    label_max_length = 75
    value_max_length = 75

    def __init__(self, *, label: str, value: str, description: Optional[str] = None):
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

        Args:
            label: A short, user-facing string to label this option to users.
                Cannot exceed 75 characters.
            value: A short string that identifies this particular option to your
                application. It will be part of the payload when this option is selected
                . Cannot exceed 75 characters.
            description: A user-facing string that provides more details about
                this option. Only supported in legacy message actions, not in blocks or
                dialogs.
        """
        self.label = label
        self.value = value
        self.description = description

    @JsonValidator(f"label attribute cannot exceed {label_max_length} characters")
    def label_length(self):
        return len(self.label) <= self.label_max_length

    @JsonValidator(f"value attribute cannot exceed {value_max_length} characters")
    def value_length(self):
        return len(self.value) <= self.value_max_length

    def to_dict(self, option_type: str = "block") -> dict:
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
                "text": PlainTextObject.direct_from_string(self.label),
                "value": self.value,
            }

    @staticmethod
    def from_single_value(value_and_label: str):
        """
        Creates a simple Option instance with the same value and label
        """
        return Option(value=value_and_label, label=value_and_label)


class OptionGroup(JsonObject):
    """
    JSON must be retrieved with an explicit option_type - the Slack API has
    different required formats in different situations
    """

    attributes = {}  # no attributes because to_dict has unique implementations

    label_max_length = 75
    options_max_length = 100

    def __init__(self, *, label: str, options: List[Option]):
        """
        Create a group of Option objects - pass in a label (that will be part of the
        UI) and a list of Option objects.

        Blocks:
        https://api.slack.com/reference/messaging/composition-objects#option-group

        Dialogs:
        https://api.slack.com/dialogs#select_elements

        Legacy interactive attachments:
        https://api.slack.com/docs/interactive-message-field-guide#option_groups_to_place_within_message_menu_actions

        Args:
            label: Text to display at the top of this group of options.
            options: A list of no more than 100 Option objects.
        """  # noqa prevent flake8 blowing up on the long URL
        self.label = label
        self.options = options

    @JsonValidator(f"label attribute cannot exceed {label_max_length} characters")
    def label_length(self):
        return len(self.label) <= self.label_max_length

    @JsonValidator(f"options attribute cannot exceed {options_max_length} elements")
    def options_length(self):
        return len(self.options) <= self.options_max_length

    def to_dict(self, option_type: str = "block") -> dict:
        self.validate_json()
        if option_type == "dialog":
            return {
                "label": self.label,
                "options": extract_json(self.options, option_type),
            }
        elif option_type == "action":
            return {
                "text": self.label,
                "options": extract_json(self.options, option_type),
            }
        else:  # if option_type == "block"; this should be the most common case
            return {
                "label": PlainTextObject.direct_from_string(self.label),
                "options": extract_json(self.options, option_type),
            }
