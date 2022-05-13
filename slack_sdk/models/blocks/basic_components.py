import copy
import logging
import warnings
from typing import List, Optional, Set, Union, Sequence, Dict, Any

from slack_sdk.models import show_unknown_key_warning
from slack_sdk.models.basic_objects import (
    JsonObject,
    JsonValidator,
)
from slack_sdk.models.messages import Link

ButtonStyles = {"danger", "primary"}
DynamicSelectElementTypes = {"channels", "conversations", "users"}


class TextObject(JsonObject):
    """The interface for text objects (types: plain_text, mrkdwn)"""

    attributes = {"text", "type", "emoji"}
    logger = logging.getLogger(__name__)

    def _subtype_warning(self):  # skipcq: PYL-R0201
        warnings.warn(
            "subtype is deprecated since slackclient 2.6.0, use type instead",
            DeprecationWarning,
        )

    @property
    def subtype(self) -> Optional[str]:
        return self.type

    @classmethod
    def parse(
        cls,
        text: Union[str, Dict[str, Any], "TextObject"],
        default_type: str = "mrkdwn",
    ) -> Optional["TextObject"]:
        if not text:  # skipcq: PYL-R1705
            return None
        elif isinstance(text, str):
            if default_type == PlainTextObject.type:  # skipcq: PYL-R1705
                return PlainTextObject.from_str(text)
            else:
                return MarkdownTextObject.from_str(text)
        elif isinstance(text, dict):
            d = copy.copy(text)
            t = d.pop("type")
            if t == PlainTextObject.type:  # skipcq: PYL-R1705
                return PlainTextObject(**d)
            else:
                return MarkdownTextObject(**d)
        elif isinstance(text, TextObject):
            return text
        else:
            cls.logger.warning(
                f"Unknown type ({type(text)}) detected when parsing a TextObject"
            )
            return None

    def __init__(
        self,
        text: str,
        type: Optional[str] = None,  # skipcq: PYL-W0622
        subtype: Optional[str] = None,
        emoji: Optional[bool] = None,
        **kwargs,
    ):
        """Super class for new text "objects" used in Block kit"""
        if subtype:
            self._subtype_warning()

        self.text = text
        self.type = type if type else subtype
        self.emoji = emoji


class PlainTextObject(TextObject):
    """plain_text typed text object"""

    type = "plain_text"

    @property
    def attributes(self) -> Set[str]:
        return super().attributes.union({"emoji"})

    def __init__(self, *, text: str, emoji: Optional[bool] = None):
        """A plain text object, meaning markdown characters will not be parsed as
        formatting information.
        https://api.slack.com/reference/block-kit/composition-objects#text

        Args:
            text (required): The text for the block. This field accepts any of the standard text formatting markup
                when type is mrkdwn.
            emoji: Indicates whether emojis in a text field should be escaped into the colon emoji format.
                This field is only usable when type is plain_text.
        """
        super().__init__(text=text, type=self.type)
        self.emoji = emoji

    @staticmethod
    def from_str(text: str) -> "PlainTextObject":
        return PlainTextObject(text=text, emoji=True)

    @staticmethod
    def direct_from_string(text: str) -> Dict[str, Any]:
        """Transforms a string into the required object shape to act as a PlainTextObject"""
        return PlainTextObject.from_str(text).to_dict()


class MarkdownTextObject(TextObject):
    """mrkdwn typed text object"""

    type = "mrkdwn"

    @property
    def attributes(self) -> Set[str]:
        return super().attributes.union({"verbatim"})

    def __init__(self, *, text: str, verbatim: Optional[bool] = None):
        """A Markdown text object, meaning markdown characters will be parsed as
        formatting information.
        https://api.slack.com/reference/block-kit/composition-objects#text

        Args:
            text (required): The text for the block. This field accepts any of the standard text formatting markup
                when type is mrkdwn.
            verbatim: When set to false (as is default) URLs will be auto-converted into links,
                conversation names will be link-ified, and certain mentions will be automatically parsed.
                Using a value of true will skip any preprocessing of this nature,
                although you can still include manual parsing strings. This field is only usable when type is mrkdwn.
        """
        super().__init__(text=text, type=self.type)
        self.verbatim = verbatim

    @staticmethod
    def from_str(text: str) -> "MarkdownTextObject":
        """Transforms a string into the required object shape to act as a MarkdownTextObject"""
        return MarkdownTextObject(text=text)

    @staticmethod
    def direct_from_string(text: str) -> Dict[str, Any]:
        """Transforms a string into the required object shape to act as a MarkdownTextObject"""
        return MarkdownTextObject.from_str(text).to_dict()

    @staticmethod
    def from_link(link: Link, title: str = "") -> "MarkdownTextObject":
        """
        Transform a Link object directly into the required object shape
        to act as a MarkdownTextObject
        """
        if title:
            title = f": {title}"
        return MarkdownTextObject(text=f"{link}{title}")

    @staticmethod
    def direct_from_link(link: Link, title: str = "") -> Dict[str, Any]:
        """
        Transform a Link object directly into the required object shape
        to act as a MarkdownTextObject
        """
        return MarkdownTextObject.from_link(link, title).to_dict()


class Option(JsonObject):
    """Option object used in dialogs, legacy message actions (interactivity in attachments),
    and blocks. JSON must be retrieved with an explicit option_type - the Slack API has
    different required formats in different situations
    """

    attributes = {}  # no attributes because to_dict has unique implementations
    logger = logging.getLogger(__name__)

    label_max_length = 75
    value_max_length = 75

    def __init__(
        self,
        *,
        value: str,
        label: Optional[str] = None,
        text: Optional[Union[str, Dict[str, Any], TextObject]] = None,  # Block Kit
        description: Optional[Union[str, Dict[str, Any], TextObject]] = None,
        url: Optional[str] = None,
        **others: Dict[str, Any],
    ):
        """
        An object that represents a single selectable item in a block element (
        SelectElement, OverflowMenuElement) or dialog element
        (StaticDialogSelectElement)

        Blocks:
        https://api.slack.com/reference/block-kit/composition-objects#option

        Dialogs:
        https://api.slack.com/dialogs#select_elements

        Legacy interactive attachments:
        https://api.slack.com/legacy/interactive-message-field-guide#option_fields

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
        if text:
            # For better compatibility with Block Kit ("mrkdwn" does not work for it),
            # we've changed the default text object type to plain_text since version 3.10.0
            self._text: Optional[TextObject] = TextObject.parse(
                text=text,  # "text" here can be either a str or a TextObject
                default_type=PlainTextObject.type,
            )
            self._label: Optional[str] = None
        else:
            self._text: Optional[TextObject] = None
            self._label: Optional[str] = label

        # for backward-compatibility with version 2.0-2.5, the following fields return str values
        self.text: Optional[str] = self._text.text if self._text else None
        self.label: Optional[str] = self._label

        self.value: str = value

        # for backward-compatibility with version 2.0-2.5, the following fields return str values
        if isinstance(description, str):
            self.description = description
            self._block_description = PlainTextObject.from_str(description)
        elif isinstance(description, dict):
            self.description = description["text"]
            self._block_description = TextObject.parse(description)
        elif isinstance(description, TextObject):
            self.description = description.text
            self._block_description = description
        else:
            self.description = None
            self._block_description = None

        # A URL to load in the user's browser when the option is clicked.
        # The url attribute is only available in overflow menus.
        # Maximum length for this field is 3000 characters.
        # If you're using url, you'll still receive an interaction payload
        # and will need to send an acknowledgement response.
        self.url: Optional[str] = url
        show_unknown_key_warning(self, others)

    @JsonValidator(f"label attribute cannot exceed {label_max_length} characters")
    def _validate_label_length(self) -> bool:
        return self._label is None or len(self._label) <= self.label_max_length

    @JsonValidator(f"text attribute cannot exceed {label_max_length} characters")
    def _validate_text_length(self) -> bool:
        return (
            self._text is None
            or self._text.text is None
            or len(self._text.text) <= self.label_max_length
        )

    @JsonValidator(f"value attribute cannot exceed {value_max_length} characters")
    def _validate_value_length(self) -> bool:
        return len(self.value) <= self.value_max_length

    @classmethod
    def parse_all(
        cls, options: Optional[Sequence[Union[Dict[str, Any], "Option"]]]
    ) -> Optional[List["Option"]]:
        if options is None:
            return None
        option_objects: List[Option] = []
        for o in options:
            if isinstance(o, dict):
                d = copy.copy(o)
                option_objects.append(Option(**d))
            elif isinstance(o, Option):
                option_objects.append(o)
            else:
                cls.logger.warning(f"Unknown option object detected and skipped ({o})")
        return option_objects

    def to_dict(
        self, option_type: str = "block"
    ) -> Dict[str, Any]:  # skipcq: PYL-W0221
        """
        Different parent classes must call this with a valid value from OptionTypes -
        either "dialog", "action", or "block", so that JSON is returned in the
        correct shape.
        """
        self.validate_json()
        if option_type == "dialog":  # skipcq: PYL-R1705
            return {"label": self.label, "value": self.value}
        elif option_type == "action" or option_type == "attachment":
            # "action" can be confusing but it means a legacy message action in attachments
            # we don't remove the type name for backward compatibility though
            json = {"text": self.label, "value": self.value}
            if self.description is not None:
                json["description"] = self.description
            return json
        else:  # if option_type == "block"; this should be the most common case
            text: TextObject = self._text or PlainTextObject.from_str(self.label)
            json: Dict[str, Any] = {
                "text": text.to_dict(),
                "value": self.value,
            }
            if self._block_description:
                json["description"] = self._block_description.to_dict()
            if self.url:
                json["url"] = self.url
            return json

    @staticmethod
    def from_single_value(value_and_label: str):
        """Creates a simple Option instance with the same value and label"""
        return Option(value=value_and_label, label=value_and_label)


class OptionGroup(JsonObject):
    """
    JSON must be retrieved with an explicit option_type - the Slack API has
    different required formats in different situations
    """

    attributes = {}  # no attributes because to_dict has unique implementations
    label_max_length = 75
    options_max_length = 100
    logger = logging.getLogger(__name__)

    def __init__(
        self,
        *,
        label: Optional[Union[str, Dict[str, Any], TextObject]] = None,
        options: Sequence[Union[Dict[str, Any], Option]],
        **others: Dict[str, Any],
    ):
        """
        Create a group of Option objects - pass in a label (that will be part of the
        UI) and a list of Option objects.

        Blocks:
        https://api.slack.com/reference/block-kit/composition-objects#option-group

        Dialogs:
        https://api.slack.com/dialogs#select_elements

        Legacy interactive attachments:
        https://api.slack.com/legacy/interactive-message-field-guide#option_groups_to_place_within_message_menu_actions

        Args:
            label: Text to display at the top of this group of options.
            options: A list of no more than 100 Option objects.
        """  # noqa prevent flake8 blowing up on the long URL
        # default_type=PlainTextObject.type is for backward-compatibility
        self._label: Optional[TextObject] = TextObject.parse(
            label, default_type=PlainTextObject.type
        )
        self.label: Optional[str] = self._label.text if self._label else None
        self.options = Option.parse_all(options)  # compatible with version 2.5
        show_unknown_key_warning(self, others)

    @JsonValidator(f"label attribute cannot exceed {label_max_length} characters")
    def _validate_label_length(self):
        return self.label is None or len(self.label) <= self.label_max_length

    @JsonValidator(f"options attribute cannot exceed {options_max_length} elements")
    def _validate_options_length(self):
        return self.options is None or len(self.options) <= self.options_max_length

    @classmethod
    def parse_all(
        cls, option_groups: Optional[Sequence[Union[Dict[str, Any], "OptionGroup"]]]
    ) -> Optional[List["OptionGroup"]]:
        if option_groups is None:
            return None
        option_group_objects = []
        for o in option_groups:
            if isinstance(o, dict):
                d = copy.copy(o)
                option_group_objects.append(OptionGroup(**d))
            elif isinstance(o, OptionGroup):
                option_group_objects.append(o)
            else:
                cls.logger.warning(
                    f"Unknown option group object detected and skipped ({o})"
                )
        return option_group_objects

    def to_dict(
        self, option_type: str = "block"
    ) -> Dict[str, Any]:  # skipcq: PYL-W0221
        self.validate_json()
        dict_options = [o.to_dict(option_type) for o in self.options]
        if option_type == "dialog":  # skipcq: PYL-R1705
            return {
                "label": self.label,
                "options": dict_options,
            }
        elif option_type == "action":
            return {
                "text": self.label,
                "options": dict_options,
            }
        else:  # if option_type == "block"; this should be the most common case
            dict_label: Dict[str, Any] = self._label.to_dict()
            return {
                "label": dict_label,
                "options": dict_options,
            }


class ConfirmObject(JsonObject):
    attributes = {}  # no attributes because to_dict has unique implementations

    title_max_length = 100
    text_max_length = 300
    confirm_max_length = 30
    deny_max_length = 30

    @classmethod
    def parse(cls, confirm: Union["ConfirmObject", Dict[str, Any]]):
        if confirm:
            if isinstance(confirm, ConfirmObject):  # skipcq: PYL-R1705
                return confirm
            elif isinstance(confirm, dict):
                return ConfirmObject(**confirm)
            else:
                # Not yet implemented: show some warning here
                return None
        return None

    def __init__(
        self,
        *,
        title: Union[str, Dict[str, Any], PlainTextObject],
        text: Union[str, Dict[str, Any], TextObject],
        confirm: Union[str, Dict[str, Any], PlainTextObject] = "Yes",
        deny: Union[str, Dict[str, Any], PlainTextObject] = "No",
        style: Optional[str] = None,
    ):
        """
        An object that defines a dialog that provides a confirmation step to any
        interactive element. This dialog will ask the user to confirm their action by
        offering a confirm and deny button.
        https://api.slack.com/reference/block-kit/composition-objects#confirm
        """
        self._title = TextObject.parse(title, default_type=PlainTextObject.type)
        self._text = TextObject.parse(text, default_type=MarkdownTextObject.type)
        self._confirm = TextObject.parse(confirm, default_type=PlainTextObject.type)
        self._deny = TextObject.parse(deny, default_type=PlainTextObject.type)
        self._style = style

        # for backward-compatibility with version 2.0-2.5, the following fields return str values
        self.title = self._title.text if self._title else None
        self.text = self._text.text if self._text else None
        self.confirm = self._confirm.text if self._confirm else None
        self.deny = self._deny.text if self._deny else None
        self.style = self._style

    @JsonValidator(f"title attribute cannot exceed {title_max_length} characters")
    def title_length(self) -> bool:
        return self._title is None or len(self._title.text) <= self.title_max_length

    @JsonValidator(f"text attribute cannot exceed {text_max_length} characters")
    def text_length(self) -> bool:
        return self._text is None or len(self._text.text) <= self.text_max_length

    @JsonValidator(f"confirm attribute cannot exceed {confirm_max_length} characters")
    def confirm_length(self) -> bool:
        return (
            self._confirm is None or len(self._confirm.text) <= self.confirm_max_length
        )

    @JsonValidator(f"deny attribute cannot exceed {deny_max_length} characters")
    def deny_length(self) -> bool:
        return self._deny is None or len(self._deny.text) <= self.deny_max_length

    @JsonValidator('style for confirm must be either "primary" or "danger"')
    def _validate_confirm_style(self) -> bool:
        return self._style is None or self._style in ["primary", "danger"]

    def to_dict(
        self, option_type: str = "block"
    ) -> Dict[str, Any]:  # skipcq: PYL-W0221
        if option_type == "action":  # skipcq: PYL-R1705
            # deliberately skipping JSON validators here - can't find documentation
            # on actual limits here
            json = {
                "ok_text": self._confirm.text
                if self._confirm and self._confirm.text != "Yes"
                else "Okay",
                "dismiss_text": self._deny.text
                if self._deny and self._deny.text != "No"
                else "Cancel",
            }
            if self._title:
                json["title"] = self._title.text
            if self._text:
                json["text"] = self._text.text
            return json

        else:
            self.validate_json()
            json = {}
            if self._title:
                json["title"] = self._title.to_dict()
            if self._text:
                json["text"] = self._text.to_dict()
            if self._confirm:
                json["confirm"] = self._confirm.to_dict()
            if self._deny:
                json["deny"] = self._deny.to_dict()
            if self._style:
                json["style"] = self._style
            return json


class DispatchActionConfig(JsonObject):
    attributes = {"trigger_actions_on"}

    @classmethod
    def parse(cls, config: Union["DispatchActionConfig", Dict[str, Any]]):
        if config:
            if isinstance(config, DispatchActionConfig):  # skipcq: PYL-R1705
                return config
            elif isinstance(config, dict):
                return DispatchActionConfig(**config)
            else:
                # Not yet implemented: show some warning here
                return None
        return None

    def __init__(
        self,
        *,
        trigger_actions_on: Optional[List[Any]] = None,
    ):
        """
        Determines when a plain-text input element will return a block_actions interaction payload.
        https://api.slack.com/reference/block-kit/composition-objects#dispatch_action_config
        """
        self._trigger_actions_on = trigger_actions_on or []

    def to_dict(self) -> Dict[str, Any]:  # skipcq: PYL-W0221
        self.validate_json()
        json = {}
        if self._trigger_actions_on:
            json["trigger_actions_on"] = self._trigger_actions_on
        return json
