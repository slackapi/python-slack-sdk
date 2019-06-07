from abc import ABCMeta, abstractmethod
from enum import Enum
from typing import Any, Iterable, List, NamedTuple, Optional, Union

from ...errors import SlackObjectFormationError


class BaseObject:
    def __str__(self):
        return f"<slack.{self.__class__.__name__}>"


class JsonObject(BaseObject, metaclass=ABCMeta):
    """
    Basic object used to hold some helper methods, plus define the abstract get_json
    method
    """

    @abstractmethod
    def get_json(self, *args) -> dict:
        """
        Return this object's Slack-valid JSON representation
        :param args: Any specific formatting args (rare; generally ignored)
        :return: a Python dict - (will be encoded later)
        :raises SlackObjectFormationError if the object was not valid
        """
        pass

    @staticmethod
    def get_raw_value(possible_enum_value: Union[str, Enum]) -> Optional[str]:
        """
        Collapse an incoming value (which should be an enum, per type annotations) to a
        raw value
        :param possible_enum_value: incoming value
        :return: the primitive (string) value
        """
        if isinstance(possible_enum_value, Enum):
            return possible_enum_value.value
        else:
            return possible_enum_value

    def get_non_null_keys(self, keys: Iterable[str]) -> dict:
        """
        Construct a dictionary out of non-null keys present on this object
        """
        return {
            key: getattr(self, key, None)
            for key in keys
            if getattr(self, key, None) is not None
        }

    def __repr__(self):
        return f"<slack.{self.__class__.__name__}: {{{self.get_json()}}}>"


class IDNamePair(NamedTuple):
    """
    Simple type used to help with unpacking event data
    """

    id: str
    name: str


class Link(BaseObject):
    """
    Base class used to generate links in Slack's not-quite Markdown, not quite HTML
    syntax
    """

    def __init__(self, url: str, text: str, icon: str = None):
        self.url = url
        self.text = text
        self.icon = icon
        self.formats = {
            "slack": self.slack_flavored_markdown,
            "github": self.github_flavored_markdown,
            "plain": self.plain_text,
        }

    def __str__(self):
        return self.slack_flavored_markdown()

    def __format__(self, format_spec=None):
        return self.formats.get(format_spec, self.slack_flavored_markdown)()

    def slack_flavored_markdown(self) -> str:
        icon = f":{self.icon}: " if self.icon is not None else ""
        return f"<{self.url}{'|' if self.text else ''}{icon}{self.text}>"

    def github_flavored_markdown(self) -> str:
        return f"[{self.text}]({self.url})"

    def plain_text(self) -> str:
        return self.text


class ObjectLink(Link):
    prefix_mapping = {
        "C": "#",  # channel
        "G": "#",  # group message
        "U": "@",  # user
        "W": "@",  # workspace user (enterprise)
        "B": "@",  # bot user
        "S": "!subteam^",  # user groups, originally known as subteams
    }

    def __init__(self, object_id: str, text: str = ""):
        prefix = self.prefix_mapping.get(object_id[0].upper(), "@")
        super().__init__(f"{prefix}{object_id}", text)


class TextObject(JsonObject):
    """
    Super class for new text "objects" used in Block kit
    """

    def __init__(self, text: str, type: str):
        self.text = text
        self.type = type

    def get_json(self) -> dict:
        return {"text": self.text, "type": self.type}


class PlainTextObject(TextObject):
    """
    Text object with no formatting
    """

    def __init__(self, text: str, emoji: bool = True):
        """
        :param emoji: Whether to escape emoji in text into Slack's :emoji: format
        """
        super().__init__(text=text, type="plain_text")
        self.emoji = emoji

    def get_json(self) -> dict:
        json = super().get_json()
        json["emoji"] = self.emoji
        return json


class MarkdownTextObject(TextObject):
    def __init__(self, text: str, verbatim: bool = False):
        """
        :param verbatim: When set to false (as is default) URLs will be auto-converted
        into links, conversation names will be link-ified, and certain mentions will be
        automatically parsed.
        """
        super().__init__(text=text, type="mrkdwn")
        self.verbatim = verbatim

    def get_json(self) -> dict:
        json = super().get_json()
        json["verbatim"] = self.verbatim
        return json


class LinkTextObject(MarkdownTextObject):
    """
    Convenience class for creating a MarkdownTextObject from a Link object
    """

    def __init__(self, link: Link, title: str = ""):
        """
        :param link: The link to represent as markdown text
        :param title: An optional title to place after the hyperlink
        """
        if title:
            title = f": {title}"
        super().__init__(text=f"{link}{title}")


class ConfirmObject(JsonObject):
    def __init__(self, title: str, text: str, confirm: str = "Yes", deny: str = "No"):
        """
        An object that defines a dialog that provides a confirmation step to any
        interactive element. This dialog will ask the user to confirm their action by
        offering a confirm and deny button.
        """
        self.title = title
        self.text = text
        self.confirm = confirm
        self.deny = deny

    def get_json(self) -> dict:
        if len(self.title) > 100:
            raise SlackObjectFormationError(
                "title attribute cannot exceed 100 characters"
            )
        if len(self.text) > 300:
            raise SlackObjectFormationError(
                "text attribute cannot exceed 300 characters"
            )
        if len(self.confirm) > 30:
            raise SlackObjectFormationError(
                "confirm attribute cannot exceed 30 characters"
            )
        if len(self.deny) > 30:
            raise SlackObjectFormationError(
                "deny attribute cannot exceed 30 characters"
            )
        return {
            "title": PlainTextObject(self.title).get_json(),
            "text": MarkdownTextObject(self.text).get_json(),
            "confirm": PlainTextObject(self.confirm).get_json(),
            "deny": PlainTextObject(self.deny).get_json(),
        }


class ContainerEnum(Enum):
    """
    Enum class extended with a type-agnostic contains method - *not* a replacement
    for the __contains__ magic method - don't try to use the in operator
    """

    @classmethod
    def contains(cls, item: Any) -> bool:
        return any(item == member.value for member in cls)

    @classmethod
    def pretty_print(cls):
        return ", ".join(f'"{t.value}"' for t in cls)


class ButtonStyle(ContainerEnum):
    """
    Supply a particular button style
    """

    PRIMARY = "primary"
    DANGER = "danger"


class OptionType(ContainerEnum):
    """
    How this option should return itself as JSON; dialogs and legacy interactive
    messages use a different json key than blocks
    """

    INTERACTIVE_MESSAGE = "label"
    DIALOG = "label"
    BLOCK = "text"


class DynamicTypes(ContainerEnum):
    USERS = "users"
    CHANNELS = "channels"
    CONVERSATIONS = "conversations"


class Option(JsonObject):
    """
    Option object used in dialogs, legacy message actions, and blocks

    JSON should be retrieved with an explicit option_type - the Slack API has
    different required formats in different situations
    """

    def __init__(self, label: str, value: str):
        self.label = label
        self.value = value

    def get_json(self, option_type: Union[OptionType, str]):
        if len(self.label) > 75:
            raise SlackObjectFormationError(
                "label attribute cannot exceed 75 characters"
            )
        if len(self.value) > 75:
            raise SlackObjectFormationError(
                "value attribute cannot exceed 75 characters"
            )
        option = self.get_raw_value(option_type)
        if option == OptionType.BLOCK.value:
            return {"text": PlainTextObject(self.label).get_json(), "value": self.value}
        else:
            return {"label": self.label, "value": self.value}


class SimpleOption(Option):
    """
    Simple constructor for Option objects that don't need separate labels and values
    """

    def __init__(self, label: str):
        super().__init__(label=label, value=label)


class OptionGroup(JsonObject):
    """
    JSON should be retrieved with an explicit option_type - the Slack API has
    different required formats in different situations
    """

    def __init__(self, label: str, options: List[Option]):
        self.label = label
        self.options = options

    def get_json(self, option_type: Union[OptionType, str]) -> dict:
        if len(self.label) > 75:
            raise SlackObjectFormationError(
                "label attribute cannot exceed 75 characters"
            )
        if len(self.options) > 100:
            raise SlackObjectFormationError(
                "options attribute cannot exceed 100 items"
            )
        option = self.get_raw_value(option_type)
        if option == OptionType.BLOCK.value:
            return {
                "label": PlainTextObject(self.label).get_json(),
                "options": [option.get_json(option_type) for option in self.options],
            }
        else:
            return {
                "label": self.label,
                "options": [option.get_json(option_type) for option in self.options],
            }
