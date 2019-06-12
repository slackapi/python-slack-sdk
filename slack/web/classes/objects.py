from functools import wraps
from typing import Callable, Iterable, List, NamedTuple, Set, Union

from ...errors import SlackObjectFormationError

ButtonStyles = {"primary", "danger"}
DynamicDropdownTypes = {"users", "channels", "conversations"}


class JsonObject:
    def validate_json(self) -> None:
        """
        :raises SlackObjectFormationError if the object was not valid
        """
        for attribute in (func for func in dir(self) if not func.startswith("__")):
            method = getattr(self, attribute)
            if callable(method) and hasattr(method, "validator"):
                method()

    def __str__(self):
        return f"<slack.{self.__class__.__name__}>"

    def get_non_null_keys(self) -> dict:
        """
        Construct a dictionary out of non-null keys present on this object
        """
        return {
            key: getattr(self, key, None)
            for key in self.attributes
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

    def __repr__(self):
        return f"<slack.{self.__class__.__name__}: {{{self.get_json()}}}>"

    @property
    def attributes(self) -> Set[str]:
        return set()


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
    """
    Base class used to generate links in Slack's not-quite Markdown, not quite HTML
    syntax
    """

    def __init__(self, *, url: str, text: str):
        self.url = url
        self.text = text
        self.formats = {"slack": self.slack_flavored_markdown, "plain": self.plain_text}

    def __str__(self):
        return self.slack_flavored_markdown()

    def __format__(self, format_spec=None):
        return self.formats.get(format_spec, self.slack_flavored_markdown)()

    def slack_flavored_markdown(self) -> str:
        return f"<{self.url}{'|' if self.text else ''}{self.text}>"

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

    def __init__(self, *, object_id: str, text: str = ""):
        prefix = self.prefix_mapping.get(object_id[0].upper(), "@")
        super().__init__(url=f"{prefix}{object_id}", text=text)


class TextObject(JsonObject):
    """
    Super class for new text "objects" used in Block kit
    """

    attributes = {"text", "type"}

    def __init__(self, *, text: str, type: str):
        self.text = text
        self.type = type


class PlainTextObject(TextObject):
    """
    Text object with no formatting
    """

    @property
    def attributes(self) -> Set[str]:
        return super().attributes.union({"emoji"})

    def __init__(self, *, text: str, emoji: bool = True):
        """
        :param emoji: Whether to escape emoji in text into Slack's :emoji: format
        """
        super().__init__(text=text, type="plain_text")
        self.emoji = emoji

    @staticmethod
    def from_string(string: str) -> dict:
        return PlainTextObject(text=string).get_json()


class MarkdownTextObject(TextObject):
    @property
    def attributes(self) -> Set[str]:
        return super().attributes.union({"verbatim"})

    def __init__(self, *, text: str, verbatim: bool = False):
        """
        :param verbatim: When set to false (as is default) URLs will be auto-converted
        into links, conversation names will be link-ified, and certain mentions will be
        automatically parsed.
        """
        super().__init__(text=text, type="mrkdwn")
        self.verbatim = verbatim

    @staticmethod
    def from_string(string: str) -> dict:
        return MarkdownTextObject(text=string).get_json()


class LinkTextObject(MarkdownTextObject):
    """
    Convenience class for creating a MarkdownTextObject from a Link object
    """

    def __init__(self, *, link: Link, title: str = ""):
        """
        :param link: The link to represent as markdown text
        :param title: An optional title to place after the hyperlink
        """
        if title:
            title = f": {title}"
        super().__init__(text=f"{link}{title}")


class ConfirmObject(JsonObject):
    def __init__(
        self, *, title: str, text: str, confirm: str = "Yes", deny: str = "No"
    ):
        """
        An object that defines a dialog that provides a confirmation step to any
        interactive element. This dialog will ask the user to confirm their action by
        offering a confirm and deny button.
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
        return len(self.text) <= 300

    @JsonValidator("confirm attribute cannot exceed 30 characters")
    def confirm_length(self):
        return len(self.confirm) <= 30

    @JsonValidator("deny attribute cannot exceed 30 characters")
    def deny_length(self):
        return len(self.deny) <= 30

    def get_json(self) -> dict:
        self.validate_json()
        return {
            "title": PlainTextObject(text=self.title).get_json(),
            "text": MarkdownTextObject(text=self.text).get_json(),
            "confirm": PlainTextObject(text=self.confirm).get_json(),
            "deny": PlainTextObject(text=self.deny).get_json(),
        }


class Option(JsonObject):
    """
    Option object used in dialogs, legacy message actions, and blocks

    JSON should be retrieved with an explicit option_type - the Slack API has
    different required formats in different situations
    """

    def __init__(self, *, label: str, value: str):
        self.label = label
        self.value = value

    @JsonValidator("label attribute cannot exceed 75 characters")
    def label_length(self):
        return len(self.label) <= 75

    @JsonValidator("value attribute cannot exceed 75 characters")
    def value_length(self):
        return len(self.value) <= 75

    def get_json(self, option_type: str):
        self.validate_json()
        if option_type == "text":
            return {
                "text": PlainTextObject(text=self.label).get_json(),
                "value": self.value,
            }
        else:
            return {"label": self.label, "value": self.value}


class SimpleOption(Option):
    """
    Simple constructor for Option objects that don't need separate labels and values
    """

    def __init__(self, *, label: str):
        super().__init__(label=label, value=label)


class OptionGroup(JsonObject):
    """
    JSON should be retrieved with an explicit option_type - the Slack API has
    different required formats in different situations
    """

    def __init__(self, *, label: str, options: List[Option]):
        self.label = label
        self.options = options

    @JsonValidator("label attribute cannot exceed 75 characters")
    def label_length(self):
        return len(self.label) <= 75

    @JsonValidator("options attribute cannot exceed 100 elements")
    def options_length(self):
        return len(self.options) <= 100

    def get_json(self, option_type: str) -> dict:
        if option_type == "text":
            return {
                "label": PlainTextObject(text=self.label).get_json(),
                "options": extract_json(self.options, Option, option_type),
            }
        else:
            return {
                "label": self.label,
                "options": extract_json(self.options, Option, option_type),
            }


OptionTypes = (Option, OptionGroup)


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
    except TypeError:
        return (
            item_or_items.get_json(*format_args)
            if isinstance(item_or_items, expected_object)
            else item_or_items
        )
