import copy
import logging
import re
import warnings
from abc import ABCMeta
from typing import List, Optional, Set, Union

from . import EnumValidator, JsonObject, JsonValidator, show_unknown_key_warning
from .objects import (
    ButtonStyles,
    ConfirmObject,
    DispatchActionConfig,
    Option,
    OptionGroup,
    TextObject,
    PlainTextObject,
    MarkdownTextObject,
)


# -------------------------------------------------
# Base Classes
# -------------------------------------------------


class BlockElement(JsonObject, metaclass=ABCMeta):
    """Block Elements are things that exists inside of your Blocks.
    https://api.slack.com/reference/block-kit/block-elements
    """

    attributes = {"type"}
    logger = logging.getLogger(__name__)

    @staticmethod
    def _subtype_warning():
        warnings.warn(
            "subtype is deprecated since slackclient 2.6.0, use type instead",
            DeprecationWarning,
        )

    @property
    def subtype(self) -> Optional[str]:
        return self.type

    def __init__(
        self,
        *,
        type: Optional[str] = None,  # skipcq: PYL-W0622
        subtype: Optional[str] = None,
        **others: dict,
    ):
        if subtype:
            self._subtype_warning()
        self.type = type if type else subtype
        show_unknown_key_warning(self, others)

    @classmethod
    def parse(
        cls, block_element: Union[dict, "BlockElement"]
    ) -> Optional["BlockElement"]:
        if block_element is None:  # skipcq: PYL-R1705
            return None
        elif isinstance(block_element, dict):
            if "type" in block_element:
                d = copy.copy(block_element)
                t = d.pop("type")
                if t == PlainTextObject.type:  # skipcq: PYL-R1705
                    return PlainTextObject(**d)
                elif t == MarkdownTextObject.type:
                    return MarkdownTextObject(**d)
                elif t == ImageElement.type:
                    return ImageElement(**d)
                elif t == ButtonElement.type:
                    return ButtonElement(**d)
                elif t == StaticSelectElement.type:
                    return StaticSelectElement(**d)
                elif t == StaticMultiSelectElement.type:
                    return StaticMultiSelectElement(**d)
                elif t == ExternalDataSelectElement.type:
                    return ExternalDataSelectElement(**d)
                elif t == ExternalDataMultiSelectElement.type:
                    return ExternalDataMultiSelectElement(**d)
                elif t == UserSelectElement.type:
                    return UserSelectElement(**d)
                elif t == UserMultiSelectElement.type:
                    return UserMultiSelectElement(**d)
                elif t == ConversationSelectElement.type:
                    return ConversationSelectElement(**d)
                elif t == ConversationMultiSelectElement.type:
                    return ConversationMultiSelectElement(**d)
                elif t == ChannelSelectElement.type:
                    return ChannelSelectElement(**d)
                elif t == ChannelMultiSelectElement.type:
                    return ChannelMultiSelectElement(**d)
                elif t == PlainTextInputElement.type:
                    return PlainTextInputElement(**d)
                elif t == RadioButtonsElement.type:
                    return RadioButtonsElement(**d)
                elif t == CheckboxesElement.type:
                    return CheckboxesElement(**d)
                elif t == OverflowMenuElement.type:
                    return OverflowMenuElement(**d)
                elif t == DatePickerElement.type:
                    return DatePickerElement(**d)
                else:
                    cls.logger.warning(
                        f"Unknown element detected and skipped ({block_element})"
                    )
                    return None
            else:
                cls.logger.warning(
                    f"Unknown element detected and skipped ({block_element})"
                )
                return None
        elif isinstance(block_element, (TextObject, BlockElement)):
            return block_element
        else:
            cls.logger.warning(
                f"Unknown element detected and skipped ({block_element})"
            )
            return None

    @classmethod
    def parse_all(
        cls, block_elements: List[Union[dict, "BlockElement"]]
    ) -> List["BlockElement"]:
        return [cls.parse(e) for e in block_elements or []]


# -------------------------------------------------
# Interactive Block Elements
# -------------------------------------------------


class InteractiveElement(BlockElement):
    action_id_max_length = 255

    @property
    def attributes(self) -> Set[str]:
        return super().attributes.union({"alt_text", "action_id"})

    def __init__(
        self,
        *,
        action_id: Optional[str] = None,
        type: Optional[str] = None,  # skipcq: PYL-W0622
        subtype: Optional[str] = None,
        **others: dict,
    ):
        if subtype:
            self._subtype_warning()
        super().__init__(type=type or subtype)
        show_unknown_key_warning(self, others)

        self.action_id = action_id

    @JsonValidator(
        f"action_id attribute cannot exceed {action_id_max_length} characters"
    )
    def _validate_action_id_length(self):
        return (
            self.action_id is None or len(self.action_id) <= self.action_id_max_length
        )


class InputInteractiveElement(InteractiveElement, metaclass=ABCMeta):
    placeholder_max_length = 150

    attributes = {"type", "action_id", "placeholder", "confirm"}

    @staticmethod
    def _subtype_warning():
        warnings.warn(
            "subtype is deprecated since slackclient 2.6.0, use type instead",
            DeprecationWarning,
        )

    @property
    def subtype(self) -> Optional[str]:
        return self.type

    def __init__(
        self,
        *,
        action_id: Optional[str] = None,
        placeholder: Union[str, TextObject] = None,
        type: Optional[str] = None,  # skipcq: PYL-W0622
        subtype: Optional[str] = None,
        confirm: Optional[Union[dict, ConfirmObject]] = None,
        **others: dict,
    ):
        """InteractiveElement that is usable in input blocks"""
        if subtype:
            self._subtype_warning()
        super().__init__(action_id=action_id, type=type or subtype)
        show_unknown_key_warning(self, others)

        self.placeholder = TextObject.parse(placeholder)
        self.confirm = ConfirmObject.parse(confirm)

    @JsonValidator(
        f"placeholder attribute cannot exceed {placeholder_max_length} characters"
    )
    def _validate_placeholder_length(self):
        return (
            self.placeholder is None
            or self.placeholder.text is None
            or len(self.placeholder.text) <= self.placeholder_max_length
        )


# -------------------------------------------------
# Button
# -------------------------------------------------


class ButtonElement(InteractiveElement):
    type = "button"
    text_max_length = 75
    url_max_length = 3000
    value_max_length = 2000

    @property
    def attributes(self) -> Set[str]:
        return super().attributes.union({"text", "url", "value", "style", "confirm"})

    def __init__(
        self,
        *,
        text: Union[str, dict, TextObject],
        action_id: Optional[str] = None,
        url: Optional[str] = None,
        value: Optional[str] = None,
        style: Optional[str] = None,  # primary, danger
        confirm: Optional[Union[dict, ConfirmObject]] = None,
        **others: dict,
    ):
        """An interactive element that inserts a button. The button can be a trigger for
        anything from opening a simple link to starting a complex workflow.
        https://api.slack.com/reference/block-kit/block-elements#button
        """
        super().__init__(action_id=action_id, type=self.type)
        show_unknown_key_warning(self, others)

        # NOTE: default_type=PlainTextObject.type here is only for backward-compatibility with version 2.5.0
        self.text = TextObject.parse(text, default_type=PlainTextObject.type)
        self.url = url
        self.value = value
        self.style = style
        self.confirm = ConfirmObject.parse(confirm)

    @JsonValidator(f"text attribute cannot exceed {text_max_length} characters")
    def _validate_text_length(self):
        return (
            self.text is None
            or self.text.text is None
            or len(self.text.text) <= self.text_max_length
        )

    @JsonValidator(f"url attribute cannot exceed {url_max_length} characters")
    def _validate_url_length(self):
        return self.url is None or len(self.url) <= self.url_max_length

    @JsonValidator(f"value attribute cannot exceed {value_max_length} characters")
    def _validate_value_length(self):
        return self.value is None or len(self.value) <= self.value_max_length

    @EnumValidator("style", ButtonStyles)
    def _validate_style_valid(self):
        return self.style is None or self.style in ButtonStyles


class LinkButtonElement(ButtonElement):
    def __init__(
        self,
        *,
        text: str,
        url: str,
        action_id: Optional[str] = None,
        style: Optional[str] = None,
        **others: dict,
    ):
        """A simple button that simply opens a given URL. You will still receive an
        interaction payload and will need to send an acknowledgement response.
        This is a helper class that makes creating links simpler.
        https://api.slack.com/reference/block-kit/block-elements#button
        """
        super().__init__(
            # NOTE: value must be always absent
            text=text,
            url=url,
            action_id=action_id,
            value=None,
            style=style,
        )
        show_unknown_key_warning(self, others)


# -------------------------------------------------
# Checkboxes
# -------------------------------------------------


class CheckboxesElement(InputInteractiveElement):
    type = "checkboxes"

    @property
    def attributes(self) -> Set[str]:
        return super().attributes.union({"options", "initial_options"})

    def __init__(
        self,
        *,
        action_id: Optional[str] = None,
        placeholder: Optional[str] = None,
        options: Optional[List[Union[dict, Option]]] = None,
        initial_options: Optional[List[Union[dict, Option]]] = None,
        confirm: Optional[Union[dict, ConfirmObject]] = None,
        **others: dict,
    ):
        """A checkbox group that allows a user to choose multiple items from a list of possible options.
        https://api.slack.com/reference/block-kit/block-elements#checkboxes
        """
        super().__init__(
            type=self.type,
            action_id=action_id,
            placeholder=TextObject.parse(placeholder, PlainTextObject.type),
            confirm=ConfirmObject.parse(confirm),
        )
        show_unknown_key_warning(self, others)

        self.options = Option.parse_all(options)
        self.initial_options = Option.parse_all(initial_options)


# -------------------------------------------------
# DatePicker
# -------------------------------------------------


class DatePickerElement(InputInteractiveElement):
    type = "datepicker"

    @property
    def attributes(self) -> Set[str]:
        return super().attributes.union({"initial_date"})

    def __init__(
        self,
        *,
        action_id: Optional[str] = None,
        placeholder: Optional[Union[str, dict, TextObject]] = None,
        initial_date: Optional[str] = None,
        confirm: Optional[Union[dict, ConfirmObject]] = None,
        **others: dict,
    ):
        """
        An element which lets users easily select a date from a calendar style UI.
        Date picker elements can be used inside of SectionBlocks and ActionsBlocks.
        https://api.slack.com/reference/block-kit/block-elements#datepicker
        """
        super().__init__(
            type=self.type,
            action_id=action_id,
            placeholder=TextObject.parse(placeholder, PlainTextObject.type),
            confirm=ConfirmObject.parse(confirm),
        )
        show_unknown_key_warning(self, others)

        self.initial_date = initial_date

    @JsonValidator("initial_date attribute must be in format 'YYYY-MM-DD'")
    def _validate_initial_date_valid(self):
        return self.initial_date is None or re.match(
            r"\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])", self.initial_date
        )


# -------------------------------------------------
# Image
# -------------------------------------------------


class ImageElement(BlockElement):
    type = "image"
    image_url_max_length = 3000
    alt_text_max_length = 2000

    @property
    def attributes(self) -> Set[str]:
        return super().attributes.union({"alt_text", "image_url"})

    def __init__(
        self,
        *,
        image_url: Optional[str] = None,
        alt_text: Optional[str] = None,
        **others: dict,
    ):
        """An element to insert an image - this element can be used in section and
        context blocks only. If you want a block with only an image in it,
        you're looking for the image block.
        https://api.slack.com/reference/block-kit/block-elements#image
        """
        super().__init__(type=self.type)
        show_unknown_key_warning(self, others)

        self.image_url = image_url
        self.alt_text = alt_text

    @JsonValidator(
        f"image_url attribute cannot exceed {image_url_max_length} characters"
    )
    def _validate_image_url_length(self):
        return len(self.image_url) <= self.image_url_max_length

    @JsonValidator(f"alt_text attribute cannot exceed {alt_text_max_length} characters")
    def _validate_alt_text_length(self):
        return len(self.alt_text) <= self.alt_text_max_length


# -------------------------------------------------
# Static Select
# -------------------------------------------------


class StaticSelectElement(InputInteractiveElement):
    type = "static_select"
    options_max_length = 100
    option_groups_max_length = 100

    @property
    def attributes(self) -> Set[str]:
        return super().attributes.union({"options", "option_groups", "initial_option"})

    def __init__(
        self,
        *,
        placeholder: Optional[Union[str, dict, TextObject]] = None,
        action_id: Optional[str] = None,
        options: Optional[List[Union[dict, Option]]] = None,
        option_groups: Optional[List[Union[dict, OptionGroup]]] = None,
        initial_option: Optional[Union[dict, Option]] = None,
        confirm: Optional[Union[dict, ConfirmObject]] = None,
        **others: dict,
    ):
        """This is the simplest form of select menu, with a static list of options passed in when defining the element.
        https://api.slack.com/reference/block-kit/block-elements#static_select
        """
        super().__init__(
            type=self.type,
            action_id=action_id,
            placeholder=TextObject.parse(placeholder, PlainTextObject.type),
            confirm=ConfirmObject.parse(confirm),
        )
        show_unknown_key_warning(self, others)

        self.options = options
        self.option_groups = option_groups
        self.initial_option = initial_option

    @JsonValidator(f"options attribute cannot exceed {options_max_length} elements")
    def _validate_options_length(self):
        return self.options is None or len(self.options) <= self.options_max_length

    @JsonValidator(
        f"option_groups attribute cannot exceed {option_groups_max_length} elements"
    )
    def _validate_option_groups_length(self):
        return (
            self.option_groups is None
            or len(self.option_groups) <= self.option_groups_max_length
        )

    @JsonValidator("options and option_groups cannot both be specified")
    def _validate_options_and_option_groups_both_specified(self):
        return not (self.options is not None and self.option_groups is not None)

    @JsonValidator("options or option_groups must be specified")
    def _validate_neither_options_or_option_groups_is_specified(self):
        return self.options is not None or self.option_groups is not None


class StaticMultiSelectElement(InputInteractiveElement):
    type = "multi_static_select"
    options_max_length = 100
    option_groups_max_length = 100

    @property
    def attributes(self) -> Set[str]:
        return super().attributes.union(
            {"options", "option_groups", "initial_options", "max_selected_items"}
        )

    def __init__(
        self,
        *,
        placeholder: Optional[Union[str, dict, TextObject]] = None,
        action_id: Optional[str] = None,
        options: Optional[List[Option]] = None,
        option_groups: Optional[List[OptionGroup]] = None,
        initial_options: Optional[List[Option]] = None,
        confirm: Optional[Union[dict, ConfirmObject]] = None,
        max_selected_items: Optional[int] = None,
        **others: dict,
    ):
        """
        This is the simplest form of select menu, with a static list of options passed in when defining the element.
        https://api.slack.com/reference/block-kit/block-elements#static_multi_select
        """
        super().__init__(
            type=self.type,
            action_id=action_id,
            placeholder=TextObject.parse(placeholder, PlainTextObject.type),
            confirm=ConfirmObject.parse(confirm),
        )
        show_unknown_key_warning(self, others)

        self.options = Option.parse_all(options)
        self.option_groups = OptionGroup.parse_all(option_groups)
        self.initial_options = Option.parse_all(initial_options)
        self.max_selected_items = max_selected_items

    @JsonValidator(f"options attribute cannot exceed {options_max_length} elements")
    def _validate_options_length(self):
        return self.options is None or len(self.options) <= self.options_max_length

    @JsonValidator(
        f"option_groups attribute cannot exceed {option_groups_max_length} elements"
    )
    def _validate_option_groups_length(self):
        return (
            self.option_groups is None
            or len(self.option_groups) <= self.option_groups_max_length
        )

    @JsonValidator("options and option_groups cannot both be specified")
    def _validate_options_and_option_groups_both_specified(self):
        return self.options is None or self.option_groups is None

    @JsonValidator("options or option_groups must be specified")
    def _validate_neither_options_or_option_groups_is_specified(self):
        return self.options is not None or self.option_groups is not None


# SelectElement will be deprecated in version 3, use StaticSelectElement instead
class SelectElement(InputInteractiveElement):
    type = "static_select"
    options_max_length = 100
    option_groups_max_length = 100

    @property
    def attributes(self) -> Set[str]:
        return super().attributes.union({"options", "option_groups", "initial_option"})

    def __init__(
        self,
        *,
        action_id: Optional[str] = None,
        placeholder: Optional[str] = None,
        options: Optional[List[Option]] = None,
        option_groups: Optional[List[OptionGroup]] = None,
        initial_option: Optional[Option] = None,
        confirm: Optional[Union[dict, ConfirmObject]] = None,
        **others: dict,
    ):
        """This is the simplest form of select menu, with a static list of options passed in when defining the element.
        https://api.slack.com/reference/block-kit/block-elements#static_select
        """
        super().__init__(
            type=self.type,
            action_id=action_id,
            placeholder=TextObject.parse(placeholder, PlainTextObject.type),
            confirm=ConfirmObject.parse(confirm),
        )
        show_unknown_key_warning(self, others)

        self.options = options
        self.option_groups = option_groups
        self.initial_option = initial_option

    @JsonValidator(f"options attribute cannot exceed {options_max_length} elements")
    def _validate_options_length(self):
        return self.options is None or len(self.options) <= self.options_max_length

    @JsonValidator(
        f"option_groups attribute cannot exceed {option_groups_max_length} elements"
    )
    def _validate_option_groups_length(self):
        return (
            self.option_groups is None
            or len(self.option_groups) <= self.option_groups_max_length
        )

    @JsonValidator("options and option_groups cannot both be specified")
    def _validate_options_and_option_groups_both_specified(self):
        return not (self.options is not None and self.option_groups is not None)

    @JsonValidator("options or option_groups must be specified")
    def _validate_neither_options_or_option_groups_is_specified(self):
        return self.options is not None or self.option_groups is not None


# -------------------------------------------------
# External Data Source Select
# -------------------------------------------------


class ExternalDataSelectElement(InputInteractiveElement):
    type = "external_select"

    @property
    def attributes(self) -> Set[str]:
        return super().attributes.union({"min_query_length", "initial_option"})

    def __init__(
        self,
        *,
        action_id: Optional[str] = None,
        placeholder: Union[str, TextObject] = None,
        initial_option: Union[Optional[Option], Optional[OptionGroup]] = None,
        min_query_length: Optional[int] = None,
        confirm: Optional[Union[dict, ConfirmObject]] = None,
        **others: dict,
    ):
        """
        This select menu will load its options from an external data source, allowing
        for a dynamic list of options.
        https://api.slack.com/reference/block-kit/block-elements#external_select
        """
        super().__init__(
            type=self.type,
            action_id=action_id,
            placeholder=TextObject.parse(placeholder, PlainTextObject.type),
            confirm=ConfirmObject.parse(confirm),
        )
        show_unknown_key_warning(self, others)

        self.min_query_length = min_query_length
        self.initial_option = initial_option


class ExternalDataMultiSelectElement(InputInteractiveElement):
    type = "multi_external_select"

    @property
    def attributes(self) -> Set[str]:
        return super().attributes.union(
            {"min_query_length", "initial_options", "max_selected_items"}
        )

    def __init__(
        self,
        *,
        placeholder: Optional[Union[str, dict, TextObject]] = None,
        action_id: Optional[str] = None,
        min_query_length: Optional[int] = None,
        initial_options: Optional[List[Union[dict, Option]]] = None,
        confirm: Optional[Union[dict, ConfirmObject]] = None,
        max_selected_items: Optional[int] = None,
        **others: dict,
    ):
        """
        This select menu will load its options from an external data source, allowing
        for a dynamic list of options.
        https://api.slack.com/reference/block-kit/block-elements#external-select
        """
        super().__init__(
            type=self.type,
            action_id=action_id,
            placeholder=TextObject.parse(placeholder, PlainTextObject.type),
            confirm=ConfirmObject.parse(confirm),
        )
        show_unknown_key_warning(self, others)

        self.min_query_length = min_query_length
        self.initial_options = Option.parse_all(initial_options)
        self.max_selected_items = max_selected_items


# -------------------------------------------------
# Users Select
# -------------------------------------------------


class UserSelectElement(InputInteractiveElement):
    type = "users_select"

    @property
    def attributes(self) -> Set[str]:
        return super().attributes.union({"initial_user"})

    def __init__(
        self,
        *,
        placeholder: Optional[Union[str, dict, TextObject]] = None,
        action_id: Optional[str] = None,
        initial_user: Optional[str] = None,
        confirm: Optional[Union[dict, ConfirmObject]] = None,
        **others: dict,
    ):
        """
        This select menu will populate its options with a list of Slack users visible to
        the current user in the active workspace.
        https://api.slack.com/reference/block-kit/block-elements#users_select
        """
        super().__init__(
            type=self.type,
            action_id=action_id,
            placeholder=TextObject.parse(placeholder, PlainTextObject.type),
            confirm=ConfirmObject.parse(confirm),
        )
        show_unknown_key_warning(self, others)

        self.initial_user = initial_user


class UserMultiSelectElement(InputInteractiveElement):
    type = "multi_users_select"

    @property
    def attributes(self) -> Set[str]:
        return super().attributes.union({"initial_users", "max_selected_items"})

    def __init__(
        self,
        *,
        action_id: Optional[str] = None,
        placeholder: Optional[Union[str, dict, TextObject]] = None,
        initial_users: Optional[List[str]] = None,
        confirm: Optional[Union[dict, ConfirmObject]] = None,
        max_selected_items: Optional[int] = None,
        **others: dict,
    ):
        """
        This select menu will populate its options with a list of Slack users visible to
        the current user in the active workspace.
        https://api.slack.com/reference/block-kit/block-elements#users_multi_select
        """
        super().__init__(
            type=self.type,
            action_id=action_id,
            placeholder=TextObject.parse(placeholder, PlainTextObject.type),
            confirm=ConfirmObject.parse(confirm),
        )
        show_unknown_key_warning(self, others)

        self.initial_users = initial_users
        self.max_selected_items = max_selected_items


# -------------------------------------------------
# Conversations Select
# -------------------------------------------------


class ConversationFilter(JsonObject):
    attributes = {"include", "exclude_bot_users"}
    logger = logging.getLogger(__name__)

    def __init__(
        self,
        *,
        include: Optional[List[str]] = None,
        exclude_bot_users: Optional[bool] = None,
    ):
        self.include = include
        self.exclude_bot_users = exclude_bot_users

    @classmethod
    def parse(cls, filter: Union[dict, "ConversationFilter"]):  # skipcq: PYL-W0622
        if filter is None:  # skipcq: PYL-R1705
            return None
        elif isinstance(filter, ConversationFilter):
            return filter
        elif isinstance(filter, dict):
            d = copy.copy(filter)
            return ConversationFilter(**d)
        else:
            cls.logger.warning(
                f"Unknown conversation filter object detected and skipped ({filter})"
            )
            return None


class ConversationSelectElement(InputInteractiveElement):
    type = "conversations_select"

    @property
    def attributes(self) -> Set[str]:
        return super().attributes.union(
            {
                "initial_conversation",
                "response_url_enabled",
                "filter",
                "default_to_current_conversation",
            }
        )

    def __init__(
        self,
        *,
        placeholder: Optional[Union[str, dict, TextObject]] = None,
        action_id: Optional[str] = None,
        initial_conversation: Optional[str] = None,
        confirm: Optional[Union[dict, ConfirmObject]] = None,
        response_url_enabled: Optional[bool] = None,
        default_to_current_conversation: Optional[bool] = None,
        filter: Optional[ConversationFilter] = None,  # skipcq: PYL-W0622
        **others: dict,
    ):
        """
        This select menu will populate its options with a list of public and private
        channels, DMs, and MPIMs visible to the current user in the active workspace.
        https://api.slack.com/reference/block-kit/block-elements#conversation_select
        """
        super().__init__(
            type=self.type,
            action_id=action_id,
            placeholder=TextObject.parse(placeholder, PlainTextObject.type),
            confirm=ConfirmObject.parse(confirm),
        )
        show_unknown_key_warning(self, others)

        self.initial_conversation = initial_conversation
        self.response_url_enabled = response_url_enabled
        self.default_to_current_conversation = default_to_current_conversation
        self.filter = filter


class ConversationMultiSelectElement(InputInteractiveElement):
    type = "multi_conversations_select"

    @property
    def attributes(self) -> Set[str]:
        return super().attributes.union(
            {
                "initial_conversations",
                "max_selected_items",
                "default_to_current_conversation",
                "filter",
            }
        )

    def __init__(
        self,
        *,
        placeholder: Optional[Union[str, dict, TextObject]] = None,
        action_id: Optional[str] = None,
        initial_conversations: Optional[List[str]] = None,
        confirm: Optional[Union[dict, ConfirmObject]] = None,
        max_selected_items: Optional[int] = None,
        default_to_current_conversation: Optional[bool] = None,
        filter: Optional[Union[dict, ConversationFilter]] = None,  # skipcq: PYL-W0622
        **others: dict,
    ):
        """
        This multi-select menu will populate its options with a list of public and private channels,
        DMs, and MPIMs visible to the current user in the active workspace.
        https://api.slack.com/reference/block-kit/block-elements#conversation_multi_select
        """
        super().__init__(
            type=self.type,
            action_id=action_id,
            placeholder=TextObject.parse(placeholder, PlainTextObject.type),
            confirm=ConfirmObject.parse(confirm),
        )
        show_unknown_key_warning(self, others)

        self.initial_conversations = initial_conversations
        self.max_selected_items = max_selected_items
        self.default_to_current_conversation = default_to_current_conversation
        self.filter = ConversationFilter.parse(filter)


# -------------------------------------------------
# Channels Select
# -------------------------------------------------


class ChannelSelectElement(InputInteractiveElement):
    type = "channels_select"

    @property
    def attributes(self) -> Set[str]:
        return super().attributes.union({"initial_channel", "response_url_enabled"})

    def __init__(
        self,
        *,
        placeholder: Optional[Union[str, dict, TextObject]] = None,
        action_id: Optional[str] = None,
        initial_channel: Optional[str] = None,
        confirm: Optional[Union[dict, ConfirmObject]] = None,
        response_url_enabled: Optional[bool] = None,
        **others: dict,
    ):
        """
        This select menu will populate its options with a list of public channels
        visible to the current user in the active workspace.
        https://api.slack.com/reference/block-kit/block-elements#channel_select
        """
        super().__init__(
            type=self.type,
            action_id=action_id,
            placeholder=TextObject.parse(placeholder, PlainTextObject.type),
            confirm=ConfirmObject.parse(confirm),
        )
        show_unknown_key_warning(self, others)

        self.initial_channel = initial_channel
        self.response_url_enabled = response_url_enabled


class ChannelMultiSelectElement(InputInteractiveElement):
    type = "multi_channels_select"

    @property
    def attributes(self) -> Set[str]:
        return super().attributes.union({"initial_channels", "max_selected_items"})

    def __init__(
        self,
        *,
        placeholder: Optional[Union[str, dict, TextObject]] = None,
        action_id: Optional[str] = None,
        initial_channels: Optional[List[str]] = None,
        confirm: Optional[Union[dict, ConfirmObject]] = None,
        max_selected_items: Optional[int] = None,
        **others: dict,
    ):
        """
        This multi-select menu will populate its options with a list of public channels visible
        to the current user in the active workspace.
        https://api.slack.com/reference/block-kit/block-elements#channel_multi_select
        """
        super().__init__(
            type=self.type,
            action_id=action_id,
            placeholder=TextObject.parse(placeholder, PlainTextObject.type),
            confirm=ConfirmObject.parse(confirm),
        )
        show_unknown_key_warning(self, others)

        self.initial_channels = initial_channels
        self.max_selected_items = max_selected_items


# -------------------------------------------------
# Input Elements
# -------------------------------------------------


class PlainTextInputElement(InputInteractiveElement):
    type = "plain_text_input"

    @property
    def attributes(self) -> Set[str]:
        return super().attributes.union(
            {
                "initial_value",
                "multiline",
                "min_length",
                "max_length",
                "dispatch_action_config",
            }
        )

    def __init__(
        self,
        *,
        action_id: Optional[str] = None,
        placeholder: Optional[Union[str, dict, TextObject]] = None,
        confirm: Optional[Union[dict, ConfirmObject]] = None,
        initial_value: Optional[str] = None,
        multiline: Optional[bool] = None,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        dispatch_action_config: Optional[Union[dict, DispatchActionConfig]] = None,
        **others: dict,
    ):
        """
        An element which lets users easily select a date from a calendar style UI.
        Date picker elements can be used inside of SectionBlocks and ActionsBlocks.
        https://api.slack.com/reference/block-kit/block-elements#datepicker
        """
        super().__init__(
            type=self.type,
            action_id=action_id,
            placeholder=TextObject.parse(placeholder, PlainTextObject.type),
            confirm=ConfirmObject.parse(confirm),
        )
        show_unknown_key_warning(self, others)

        self.initial_value = initial_value
        self.multiline = multiline
        self.min_length = min_length
        self.max_length = max_length
        self.dispatch_action_config = dispatch_action_config


# -------------------------------------------------
# Radio Buttons Select
# -------------------------------------------------


class RadioButtonsElement(InputInteractiveElement):
    type = "radio_buttons"

    @property
    def attributes(self) -> Set[str]:
        return super().attributes.union({"options", "initial_option"})

    def __init__(
        self,
        *,
        action_id: Optional[str] = None,
        placeholder: Optional[Union[str, dict, TextObject]] = None,
        options: Optional[List[Union[dict, Option]]] = None,
        initial_option: Optional[Union[dict, Option]] = None,
        confirm: Optional[Union[dict, ConfirmObject]] = None,
        **others: dict,
    ):
        """A radio button group that allows a user to choose one item from a list of possible options.
        https://api.slack.com/reference/block-kit/block-elements#radio
        """
        super().__init__(
            type=self.type,
            action_id=action_id,
            placeholder=TextObject.parse(placeholder, PlainTextObject.type),
            confirm=ConfirmObject.parse(confirm),
        )
        show_unknown_key_warning(self, others)

        self.options = options
        self.initial_option = initial_option


# -------------------------------------------------
# Overflow Menu Select
# -------------------------------------------------


class OverflowMenuElement(InteractiveElement):
    type = "overflow"
    options_min_length = 2
    options_max_length = 5

    @property
    def attributes(self) -> Set[str]:
        return super().attributes.union({"confirm", "options"})

    def __init__(
        self,
        *,
        action_id: Optional[str] = None,
        options: List[Union[Option]],
        confirm: Optional[Union[dict, ConfirmObject]] = None,
        **others: dict,
    ):
        """
        This is like a cross between a button and a select menu - when a user clicks
        on this overflow button, they will be presented with a list of options to
        choose from. Unlike the select menu, there is no typeahead field, and the
        button always appears with an ellipsis ("…") rather than customisable text.

        As such, it is usually used if you want a more compact layout than a select
        menu, or to supply a list of less visually important actions after a row of
        buttons. You can also specify simple URL links as overflow menu options,
        instead of actions.

        https://api.slack.com/reference/block-kit/block-elements#overflow
        """
        super().__init__(action_id=action_id, type=self.type)
        show_unknown_key_warning(self, others)

        self.options = options
        self.confirm = ConfirmObject.parse(confirm)

    @JsonValidator(
        f"options attribute must have between {options_min_length} "
        f"and {options_max_length} items"
    )
    def _validate_options_length(self):
        return self.options_min_length <= len(self.options) <= self.options_max_length
