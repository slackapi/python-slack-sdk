import copy
import logging
import re
import warnings
from abc import ABCMeta
from typing import List, Optional, Set, Union, Sequence

from slack_sdk.models import show_unknown_key_warning
from slack_sdk.models.basic_objects import (
    JsonObject,
    JsonValidator,
    EnumValidator,
)
from .basic_components import ButtonStyles
from .basic_components import ConfirmObject
from .basic_components import DispatchActionConfig
from .basic_components import MarkdownTextObject
from .basic_components import Option
from .basic_components import OptionGroup
from .basic_components import PlainTextObject
from .basic_components import TextObject


# -------------------------------------------------
# Block Elements
# -------------------------------------------------


class BlockElement(JsonObject, metaclass=ABCMeta):
    """Block Elements are things that exists inside of your Blocks.
    https://api.slack.com/reference/block-kit/block-elements
    """

    attributes = {"type"}
    logger = logging.getLogger(__name__)

    def _subtype_warning(self):  # skipcq: PYL-R0201
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
    ) -> Optional[Union["BlockElement", TextObject]]:
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
        cls, block_elements: Sequence[Union[dict, "BlockElement"]]
    ) -> List["BlockElement"]:
        return [cls.parse(e) for e in block_elements or []]


# -------------------------------------------------
# Interactive Block Elements
# -------------------------------------------------

# This is a base class
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
        """An interactive block element.

        We generally recommend using the concrete subclasses for better supports of available properties.
        """
        if subtype:
            self._subtype_warning()
        super().__init__(type=type or subtype)

        # Note that we don't intentionally have show_unknown_key_warning for the unknown key warnings here.
        # It's fine to pass any kwargs to the held dict here although the class does not do any validation.
        # show_unknown_key_warning(self, others)

        self.action_id = action_id

    @JsonValidator(
        f"action_id attribute cannot exceed {action_id_max_length} characters"
    )
    def _validate_action_id_length(self) -> bool:
        return (
            self.action_id is None or len(self.action_id) <= self.action_id_max_length
        )


# This is a base class
class InputInteractiveElement(InteractiveElement, metaclass=ABCMeta):
    placeholder_max_length = 150

    attributes = {"type", "action_id", "placeholder", "confirm", "focus_on_load"}

    @property
    def subtype(self) -> Optional[str]:
        return self.type

    def __init__(
        self,
        *,
        action_id: Optional[str] = None,
        placeholder: Optional[Union[str, TextObject]] = None,
        type: Optional[str] = None,  # skipcq: PYL-W0622
        subtype: Optional[str] = None,
        confirm: Optional[Union[dict, ConfirmObject]] = None,
        focus_on_load: Optional[bool] = None,
        **others: dict,
    ):
        """InteractiveElement that is usable in input blocks

        We generally recommend using the concrete subclasses for better supports of available properties.
        """
        if subtype:
            self._subtype_warning()
        super().__init__(action_id=action_id, type=type or subtype)

        # Note that we don't intentionally have show_unknown_key_warning for the unknown key warnings here.
        # It's fine to pass any kwargs to the held dict here although the class does not do any validation.
        # show_unknown_key_warning(self, others)

        self.placeholder = TextObject.parse(placeholder)
        self.confirm = ConfirmObject.parse(confirm)
        self.focus_on_load = focus_on_load

    @JsonValidator(
        f"placeholder attribute cannot exceed {placeholder_max_length} characters"
    )
    def _validate_placeholder_length(self) -> bool:
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

        Args:
            text (required): A text object that defines the button's text.
                Can only be of type: plain_text.
                Maximum length for the text in this field is 75 characters.
            action_id (required): An identifier for this action.
                You can use this when you receive an interaction payload to identify the source of the action.
                Should be unique among all other action_ids in the containing block.
                Maximum length for this field is 255 characters.
            url: A URL to load in the user's browser when the button is clicked.
                Maximum length for this field is 3000 characters.
                If you're using url, you'll still receive an interaction payload
                and will need to send an acknowledgement response.
            value: The value to send along with the interaction payload.
                Maximum length for this field is 2000 characters.
            style: Decorates buttons with alternative visual color schemes. Use this option with restraint.
                "primary" gives buttons a green outline and text, ideal for affirmation or confirmation actions.
                "primary" should only be used for one button within a set.
                "danger" gives buttons a red outline and text, and should be used when the action is destructive.
                Use "danger" even more sparingly than "primary".
                If you don't include this field, the default button style will be used.
            confirm: A confirm object that defines an optional confirmation dialog after the button is clicked.
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
    def _validate_text_length(self) -> bool:
        return (
            self.text is None
            or self.text.text is None
            or len(self.text.text) <= self.text_max_length
        )

    @JsonValidator(f"url attribute cannot exceed {url_max_length} characters")
    def _validate_url_length(self) -> bool:
        return self.url is None or len(self.url) <= self.url_max_length

    @JsonValidator(f"value attribute cannot exceed {value_max_length} characters")
    def _validate_value_length(self) -> bool:
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

        Args:
            text (required): A text object that defines the button's text.
                Can only be of type: plain_text.
                Maximum length for the text in this field is 75 characters.
            url (required): A URL to load in the user's browser when the button is clicked.
                Maximum length for this field is 3000 characters.
                If you're using url, you'll still receive an interaction payload
                and will need to send an acknowledgement response.
            action_id (required): An identifier for this action.
                You can use this when you receive an interaction payload to identify the source of the action.
                Should be unique among all other action_ids in the containing block.
                Maximum length for this field is 255 characters.
            style: Decorates buttons with alternative visual color schemes. Use this option with restraint.
                "primary" gives buttons a green outline and text, ideal for affirmation or confirmation actions.
                "primary" should only be used for one button within a set.
                "danger" gives buttons a red outline and text, and should be used when the action is destructive.
                Use "danger" even more sparingly than "primary".
                If you don't include this field, the default button style will be used.
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
        options: Optional[Sequence[Union[dict, Option]]] = None,
        initial_options: Optional[Sequence[Union[dict, Option]]] = None,
        confirm: Optional[Union[dict, ConfirmObject]] = None,
        focus_on_load: Optional[bool] = None,
        **others: dict,
    ):
        """A checkbox group that allows a user to choose multiple items from a list of possible options.
        https://api.slack.com/reference/block-kit/block-elements#checkboxes

        Args:
            action_id (required): An identifier for the action triggered when the checkbox group is changed.
                You can use this when you receive an interaction payload to identify the source of the action.
                Should be unique among all other action_ids in the containing block.
                Maximum length for this field is 255 characters.
            options (required): An array of option objects. A maximum of 10 options are allowed.
            initial_options: An array of option objects that exactly matches one or more of the options.
                These options will be selected when the checkbox group initially loads.
            confirm: A confirm object that defines an optional confirmation dialog that appears
                after clicking one of the checkboxes in this element.
            focus_on_load: Indicates whether the element will be set to auto focus within the view object.
                Only one element can be set to true. Defaults to false.
        """
        super().__init__(
            type=self.type,
            action_id=action_id,
            confirm=ConfirmObject.parse(confirm),
            focus_on_load=focus_on_load,
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
        focus_on_load: Optional[bool] = None,
        **others: dict,
    ):
        """
        An element which lets users easily select a date from a calendar style UI.
        Date picker elements can be used inside of SectionBlocks and ActionsBlocks.
        https://api.slack.com/reference/block-kit/block-elements#datepicker

        Args:
            action_id (required): An identifier for the action triggered when a menu option is selected.
                You can use this when you receive an interaction payload to identify the source of the action.
                Should be unique among all other action_ids in the containing block.
                Maximum length for this field is 255 characters.
            placeholder: A plain_text only text object that defines the placeholder text shown on the datepicker.
                Maximum length for the text in this field is 150 characters.
            initial_date: The initial date that is selected when the element is loaded.
                This should be in the format YYYY-MM-DD.
            confirm: A confirm object that defines an optional confirmation dialog
                that appears after a date is selected.
            focus_on_load: Indicates whether the element will be set to auto focus within the view object.
                Only one element can be set to true. Defaults to false.
        """
        super().__init__(
            type=self.type,
            action_id=action_id,
            placeholder=TextObject.parse(placeholder, PlainTextObject.type),
            confirm=ConfirmObject.parse(confirm),
            focus_on_load=focus_on_load,
        )
        show_unknown_key_warning(self, others)

        self.initial_date = initial_date

    @JsonValidator("initial_date attribute must be in format 'YYYY-MM-DD'")
    def _validate_initial_date_valid(self) -> bool:
        return (
            self.initial_date is None
            or re.match(
                r"\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])", self.initial_date
            )
            is not None
        )


# -------------------------------------------------
# TimePicker
# -------------------------------------------------


class TimePickerElement(InputInteractiveElement):
    type = "timepicker"

    @property
    def attributes(self) -> Set[str]:
        return super().attributes.union({"initial_time"})

    def __init__(
        self,
        *,
        action_id: Optional[str] = None,
        placeholder: Optional[Union[str, dict, TextObject]] = None,
        initial_time: Optional[str] = None,
        confirm: Optional[Union[dict, ConfirmObject]] = None,
        focus_on_load: Optional[bool] = None,
        **others: dict,
    ):
        """
        An element which allows selection of a time of day.
        On desktop clients, this time picker will take the form of a dropdown list
        with free-text entry for precise choices.
        On mobile clients, the time picker will use native time picker UIs.
        https://api.slack.com/reference/block-kit/block-elements#timepicker

        Args:
            action_id (required): An identifier for the action triggered when a time is selected.
                You can use this when you receive an interaction payload to identify the source of the action.
                Should be unique among all other action_ids in the containing block.
                Maximum length for this field is 255 characters.
            placeholder: A plain_text only text object that defines the placeholder text shown on the timepicker.
                Maximum length for the text in this field is 150 characters.
            initial_time: The initial time that is selected when the element is loaded.
                This should be in the format HH:mm, where HH is the 24-hour format of an hour (00 to 23)
                and mm is minutes with leading zeros (00 to 59), for example 22:25 for 10:25pm.
            confirm: A confirm object that defines an optional confirmation dialog
                that appears after a time is selected.
            focus_on_load: Indicates whether the element will be set to auto focus within the view object.
                Only one element can be set to true. Defaults to false.
        """
        super().__init__(
            type=self.type,
            action_id=action_id,
            placeholder=TextObject.parse(placeholder, PlainTextObject.type),
            confirm=ConfirmObject.parse(confirm),
            focus_on_load=focus_on_load,
        )
        show_unknown_key_warning(self, others)

        self.initial_time = initial_time

    @JsonValidator("initial_time attribute must be in format 'HH:mm'")
    def _validate_initial_time_valid(self) -> bool:
        return (
            self.initial_time is None
            or re.match(r"([0-1][0-9]|2[0-3]):([0-5][0-9])", self.initial_time)
            is not None
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

        Args:
            image_url (required): The URL of the image to be displayed.
            alt_text (required): A plain-text summary of the image. This should not contain any markup.
        """
        super().__init__(type=self.type)
        show_unknown_key_warning(self, others)

        self.image_url = image_url
        self.alt_text = alt_text

    @JsonValidator(
        f"image_url attribute cannot exceed {image_url_max_length} characters"
    )
    def _validate_image_url_length(self) -> bool:
        return len(self.image_url) <= self.image_url_max_length

    @JsonValidator(f"alt_text attribute cannot exceed {alt_text_max_length} characters")
    def _validate_alt_text_length(self) -> bool:
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
        options: Optional[Sequence[Union[dict, Option]]] = None,
        option_groups: Optional[Sequence[Union[dict, OptionGroup]]] = None,
        initial_option: Optional[Union[dict, Option]] = None,
        confirm: Optional[Union[dict, ConfirmObject]] = None,
        focus_on_load: Optional[bool] = None,
        **others: dict,
    ):
        """This is the simplest form of select menu, with a static list of options passed in when defining the element.
        https://api.slack.com/reference/block-kit/block-elements#static_select

        Args:
            placeholder (required): A plain_text only text object that defines the placeholder text shown on the menu.
                Maximum length for the text in this field is 150 characters.
            action_id (required): An identifier for the action triggered when a menu option is selected.
                You can use this when you receive an interaction payload to identify the source of the action.
                Should be unique among all other action_ids in the containing block.
                Maximum length for this field is 255 characters.
            options (either options or option_groups is required): An array of option objects.
                Maximum number of options is 100.
                If option_groups is specified, this field should not be.
            option_groups (either options or option_groups is required): An array of option group objects.
                Maximum number of option groups is 100.
                If options is specified, this field should not be.
            initial_option: A single option that exactly matches one of the options or option_groups.
                This option will be selected when the menu initially loads.
            confirm: A confirm object that defines an optional confirmation dialog
                that appears after a menu item is selected.
            focus_on_load: Indicates whether the element will be set to auto focus within the view object.
                Only one element can be set to true. Defaults to false.
        """
        super().__init__(
            type=self.type,
            action_id=action_id,
            placeholder=TextObject.parse(placeholder, PlainTextObject.type),
            confirm=ConfirmObject.parse(confirm),
            focus_on_load=focus_on_load,
        )
        show_unknown_key_warning(self, others)

        self.options = options
        self.option_groups = option_groups
        self.initial_option = initial_option

    @JsonValidator(f"options attribute cannot exceed {options_max_length} elements")
    def _validate_options_length(self) -> bool:
        return self.options is None or len(self.options) <= self.options_max_length

    @JsonValidator(
        f"option_groups attribute cannot exceed {option_groups_max_length} elements"
    )
    def _validate_option_groups_length(self) -> bool:
        return (
            self.option_groups is None
            or len(self.option_groups) <= self.option_groups_max_length
        )

    @JsonValidator("options and option_groups cannot both be specified")
    def _validate_options_and_option_groups_both_specified(self) -> bool:
        return not (self.options is not None and self.option_groups is not None)

    @JsonValidator("options or option_groups must be specified")
    def _validate_neither_options_or_option_groups_is_specified(self) -> bool:
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
        options: Optional[Sequence[Option]] = None,
        option_groups: Optional[Sequence[OptionGroup]] = None,
        initial_options: Optional[Sequence[Option]] = None,
        confirm: Optional[Union[dict, ConfirmObject]] = None,
        max_selected_items: Optional[int] = None,
        focus_on_load: Optional[bool] = None,
        **others: dict,
    ):
        """
        This is the simplest form of select menu, with a static list of options passed in when defining the element.
        https://api.slack.com/reference/block-kit/block-elements#static_multi_select

        Args:
            placeholder (required): A plain_text only text object that defines the placeholder text shown on the menu.
                Maximum length for the text in this field is 150 characters.
            action_id (required): An identifier for the action triggered when a menu option is selected.
                You can use this when you receive an interaction payload to identify the source of the action.
                Should be unique among all other action_ids in the containing block.
                Maximum length for this field is 255 characters.
            options (either options or option_groups is required): An array of option objects.
                Maximum number of options is 100.
                If option_groups is specified, this field should not be.
            option_groups (either options or option_groups is required): An array of option group objects.
                Maximum number of option groups is 100.
                If options is specified, this field should not be.
            initial_options: An array of option objects that exactly match one or more of the options
                within options or option_groups. These options will be selected when the menu initially loads.
            confirm: A confirm object that defines an optional confirmation dialog
                that appears before the multi-select choices are submitted.
            max_selected_items: Specifies the maximum number of items that can be selected in the menu.
                Minimum number is 1.
            focus_on_load: Indicates whether the element will be set to auto focus within the view object.
                Only one element can be set to true. Defaults to false.
        """
        super().__init__(
            type=self.type,
            action_id=action_id,
            placeholder=TextObject.parse(placeholder, PlainTextObject.type),
            confirm=ConfirmObject.parse(confirm),
            focus_on_load=focus_on_load,
        )
        show_unknown_key_warning(self, others)

        self.options = Option.parse_all(options)
        self.option_groups = OptionGroup.parse_all(option_groups)
        self.initial_options = Option.parse_all(initial_options)
        self.max_selected_items = max_selected_items

    @JsonValidator(f"options attribute cannot exceed {options_max_length} elements")
    def _validate_options_length(self) -> bool:
        return self.options is None or len(self.options) <= self.options_max_length

    @JsonValidator(
        f"option_groups attribute cannot exceed {option_groups_max_length} elements"
    )
    def _validate_option_groups_length(self) -> bool:
        return (
            self.option_groups is None
            or len(self.option_groups) <= self.option_groups_max_length
        )

    @JsonValidator("options and option_groups cannot both be specified")
    def _validate_options_and_option_groups_both_specified(self) -> bool:
        return self.options is None or self.option_groups is None

    @JsonValidator("options or option_groups must be specified")
    def _validate_neither_options_or_option_groups_is_specified(self) -> bool:
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
        options: Optional[Sequence[Option]] = None,
        option_groups: Optional[Sequence[OptionGroup]] = None,
        initial_option: Optional[Option] = None,
        confirm: Optional[Union[dict, ConfirmObject]] = None,
        focus_on_load: Optional[bool] = None,
        **others: dict,
    ):
        """This is the simplest form of select menu, with a static list of options passed in when defining the element.
        https://api.slack.com/reference/block-kit/block-elements#static_select

        Args:
            action_id (required): An identifier for the action triggered when a menu option is selected.
                You can use this when you receive an interaction payload to identify the source of the action.
                Should be unique among all other action_ids in the containing block.
                Maximum length for this field is 255 characters.
            placeholder (required): A plain_text only text object that defines the placeholder text shown on the menu.
                Maximum length for the text in this field is 150 characters.
            options (either options or option_groups is required): An array of option objects.
                Maximum number of options is 100.
                If option_groups is specified, this field should not be.
            option_groups (either options or option_groups is required): An array of option group objects.
                Maximum number of option groups is 100.
                If options is specified, this field should not be.
            initial_option: A single option that exactly matches one of the options or option_groups.
                This option will be selected when the menu initially loads.
            confirm: A confirm object that defines an optional confirmation dialog
                that appears after a menu item is selected.
            focus_on_load: Indicates whether the element will be set to auto focus within the view object.
                Only one element can be set to true. Defaults to false.
        """
        super().__init__(
            type=self.type,
            action_id=action_id,
            placeholder=TextObject.parse(placeholder, PlainTextObject.type),
            confirm=ConfirmObject.parse(confirm),
            focus_on_load=focus_on_load,
        )
        show_unknown_key_warning(self, others)

        self.options = options
        self.option_groups = option_groups
        self.initial_option = initial_option

    @JsonValidator(f"options attribute cannot exceed {options_max_length} elements")
    def _validate_options_length(self) -> bool:
        return self.options is None or len(self.options) <= self.options_max_length

    @JsonValidator(
        f"option_groups attribute cannot exceed {option_groups_max_length} elements"
    )
    def _validate_option_groups_length(self) -> bool:
        return (
            self.option_groups is None
            or len(self.option_groups) <= self.option_groups_max_length
        )

    @JsonValidator("options and option_groups cannot both be specified")
    def _validate_options_and_option_groups_both_specified(self) -> bool:
        return not (self.options is not None and self.option_groups is not None)

    @JsonValidator("options or option_groups must be specified")
    def _validate_neither_options_or_option_groups_is_specified(self) -> bool:
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
        placeholder: Optional[Union[str, TextObject]] = None,
        initial_option: Union[Optional[Option], Optional[OptionGroup]] = None,
        min_query_length: Optional[int] = None,
        confirm: Optional[Union[dict, ConfirmObject]] = None,
        focus_on_load: Optional[bool] = None,
        **others: dict,
    ):
        """
        This select menu will load its options from an external data source, allowing
        for a dynamic list of options.
        https://api.slack.com/reference/block-kit/block-elements#external_select

        Args:
            action_id (required): An identifier for the action triggered when a menu option is selected.
                You can use this when you receive an interaction payload to identify the source of the action.
                Should be unique among all other action_ids in the containing block.
                Maximum length for this field is 255 characters.
            placeholder (required): A plain_text only text object that defines the placeholder text shown on the menu.
                Maximum length for the text in this field is 150 characters.
            initial_option: A single option that exactly matches one of the options
                within the options or option_groups loaded from the external data source.
                This option will be selected when the menu initially loads.
            min_query_length: When the typeahead field is used, a request will be sent on every character change.
                If you prefer fewer requests or more fully ideated queries,
                use the min_query_length attribute to tell Slack
                the fewest number of typed characters required before dispatch.
                The default value is 3.
            confirm: A confirm object that defines an optional confirmation dialog
                that appears after a menu item is selected.
            focus_on_load: Indicates whether the element will be set to auto focus within the view object.
                Only one element can be set to true. Defaults to false.
        """
        super().__init__(
            type=self.type,
            action_id=action_id,
            placeholder=TextObject.parse(placeholder, PlainTextObject.type),
            confirm=ConfirmObject.parse(confirm),
            focus_on_load=focus_on_load,
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
        initial_options: Optional[Sequence[Union[dict, Option]]] = None,
        confirm: Optional[Union[dict, ConfirmObject]] = None,
        max_selected_items: Optional[int] = None,
        focus_on_load: Optional[bool] = None,
        **others: dict,
    ):
        """
        This select menu will load its options from an external data source, allowing
        for a dynamic list of options.
        https://api.slack.com/reference/block-kit/block-elements#external_multi_select

        Args:
            placeholder (required): A plain_text only text object that defines the placeholder text shown on the menu.
                Maximum length for the text in this field is 150 characters.
            action_id (required): An identifier for the action triggered when a menu option is selected.
                You can use this when you receive an interaction payload to identify the source of the action.
                Should be unique among all other action_ids in the containing block.
                Maximum length for this field is 255 characters.
            min_query_length: When the typeahead field is used, a request will be sent on every character change.
                If you prefer fewer requests or more fully ideated queries,
                use the min_query_length attribute to tell Slack
                the fewest number of typed characters required before dispatch.
                The default value is 3
            initial_options: An array of option objects that exactly match one or more of the options
                within options or option_groups. These options will be selected when the menu initially loads.
            confirm: A confirm object that defines an optional confirmation dialog that appears
                before the multi-select choices are submitted.
            max_selected_items: Specifies the maximum number of items that can be selected in the menu.
                Minimum number is 1.
            focus_on_load: Indicates whether the element will be set to auto focus within the view object.
                Only one element can be set to true. Defaults to false.
        """
        super().__init__(
            type=self.type,
            action_id=action_id,
            placeholder=TextObject.parse(placeholder, PlainTextObject.type),
            confirm=ConfirmObject.parse(confirm),
            focus_on_load=focus_on_load,
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
        focus_on_load: Optional[bool] = None,
        **others: dict,
    ):
        """
        This select menu will populate its options with a list of Slack users visible to
        the current user in the active workspace.
        https://api.slack.com/reference/block-kit/block-elements#users_select

        Args:
            placeholder (required): A plain_text only text object that defines the placeholder text shown on the menu.
                Maximum length for the text in this field is 150 characters.
            action_id (required): An identifier for the action triggered when a menu option is selected.
                You can use this when you receive an interaction payload to identify the source of the action.
                Should be unique among all other action_ids in the containing block.
                Maximum length for this field is 255 characters.
            initial_user: The user ID of any valid user to be pre-selected when the menu loads.
            confirm: A confirm object that defines an optional confirmation dialog
                that appears after a menu item is selected.
            focus_on_load: Indicates whether the element will be set to auto focus within the view object.
                Only one element can be set to true. Defaults to false.
        """
        super().__init__(
            type=self.type,
            action_id=action_id,
            placeholder=TextObject.parse(placeholder, PlainTextObject.type),
            confirm=ConfirmObject.parse(confirm),
            focus_on_load=focus_on_load,
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
        initial_users: Optional[Sequence[str]] = None,
        confirm: Optional[Union[dict, ConfirmObject]] = None,
        max_selected_items: Optional[int] = None,
        focus_on_load: Optional[bool] = None,
        **others: dict,
    ):
        """
        This select menu will populate its options with a list of Slack users visible to
        the current user in the active workspace.
        https://api.slack.com/reference/block-kit/block-elements#users_multi_select

        Args:
            action_id (required): An identifier for the action triggered when a menu option is selected.
                You can use this when you receive an interaction payload to identify the source of the action.
                Should be unique among all other action_ids in the containing block.
                Maximum length for this field is 255 characters.
            placeholder (required): A plain_text only text object that defines the placeholder text shown on the menu.
                Maximum length for the text in this field is 150 characters.
            initial_users: An array of user IDs of any valid users to be pre-selected when the menu loads.
            confirm: A confirm object that defines an optional confirmation dialog that appears
                before the multi-select choices are submitted.
            max_selected_items: Specifies the maximum number of items that can be selected in the menu.
                Minimum number is 1.
            focus_on_load: Indicates whether the element will be set to auto focus within the view object.
                Only one element can be set to true. Defaults to false.
        """
        super().__init__(
            type=self.type,
            action_id=action_id,
            placeholder=TextObject.parse(placeholder, PlainTextObject.type),
            confirm=ConfirmObject.parse(confirm),
            focus_on_load=focus_on_load,
        )
        show_unknown_key_warning(self, others)

        self.initial_users = initial_users
        self.max_selected_items = max_selected_items


# -------------------------------------------------
# Conversations Select
# -------------------------------------------------


class ConversationFilter(JsonObject):
    attributes = {"include", "exclude_bot_users", "exclude_external_shared_channels"}
    logger = logging.getLogger(__name__)

    def __init__(
        self,
        *,
        include: Optional[Sequence[str]] = None,
        exclude_bot_users: Optional[bool] = None,
        exclude_external_shared_channels: Optional[bool] = None,
    ):
        """Provides a way to filter the list of options in a conversations select menu
        or conversations multi-select menu.
        https://api.slack.com/reference/block-kit/composition-objects#filter_conversations

        Args:
            include: Indicates which type of conversations should be included in the list.
                When this field is provided, any conversations that do not match will be excluded.
                You should provide an array of strings from the following options:
                "im", "mpim", "private", and "public". The array cannot be empty.
            exclude_bot_users: Indicates whether to exclude bot users from conversation lists. Defaults to false.
            exclude_external_shared_channels: Indicates whether to exclude external shared channels
                from conversation lists. Defaults to false.
        """
        self.include = include
        self.exclude_bot_users = exclude_bot_users
        self.exclude_external_shared_channels = exclude_external_shared_channels

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
        focus_on_load: Optional[bool] = None,
        **others: dict,
    ):
        """
        This select menu will populate its options with a list of public and private
        channels, DMs, and MPIMs visible to the current user in the active workspace.
        https://api.slack.com/reference/block-kit/block-elements#conversation_select

        Args:
            placeholder (required): A plain_text only text object that defines the placeholder text shown on the menu.
                Maximum length for the text in this field is 150 characters.
            action_id (required): An identifier for the action triggered when a menu option is selected.
                You can use this when you receive an interaction payload to identify the source of the action.
                Should be unique among all other action_ids in the containing block.
                Maximum length for this field is 255 characters.
            initial_conversation: The ID of any valid conversation to be pre-selected when the menu loads.
                If default_to_current_conversation is also supplied, initial_conversation will take precedence.
            confirm: A confirm object that defines an optional confirmation dialog
                that appears after a menu item is selected.
            response_url_enabled: This field only works with menus in input blocks in modals.
                When set to true, the view_submission payload from the menu's parent view will contain a response_url.
                This response_url can be used for message responses. The target conversation for the message
                will be determined by the value of this select menu.
            default_to_current_conversation: Pre-populates the select menu with the conversation
                that the user was viewing when they opened the modal, if available. Default is false.
            filter: A filter object that reduces the list of available conversations using the specified criteria.
            focus_on_load: Indicates whether the element will be set to auto focus within the view object.
                Only one element can be set to true. Defaults to false.
        """
        super().__init__(
            type=self.type,
            action_id=action_id,
            placeholder=TextObject.parse(placeholder, PlainTextObject.type),
            confirm=ConfirmObject.parse(confirm),
            focus_on_load=focus_on_load,
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
        initial_conversations: Optional[Sequence[str]] = None,
        confirm: Optional[Union[dict, ConfirmObject]] = None,
        max_selected_items: Optional[int] = None,
        default_to_current_conversation: Optional[bool] = None,
        filter: Optional[Union[dict, ConversationFilter]] = None,  # skipcq: PYL-W0622
        focus_on_load: Optional[bool] = None,
        **others: dict,
    ):
        """
        This multi-select menu will populate its options with a list of public and private channels,
        DMs, and MPIMs visible to the current user in the active workspace.
        https://api.slack.com/reference/block-kit/block-elements#conversation_multi_select

        Args:
            placeholder (required): A plain_text only text object that defines the placeholder text shown on the menu.
                Maximum length for the text in this field is 150 characters.
            action_id (required): An identifier for the action triggered when a menu option is selected.
                You can use this when you receive an interaction payload to identify the source of the action.
                Should be unique among all other action_ids in the containing block.
                Maximum length for this field is 255 characters.
            initial_conversations: An array of one or more IDs of any valid conversations to be pre-selected
                when the menu loads. If default_to_current_conversation is also supplied,
                initial_conversations will be ignored.
            confirm: A confirm object that defines an optional confirmation dialog that appears
                before the multi-select choices are submitted.
            max_selected_items: Specifies the maximum number of items that can be selected in the menu.
                Minimum number is 1.
            default_to_current_conversation: Pre-populates the select menu with the conversation that
                the user was viewing when they opened the modal, if available. Default is false.
            filter: A filter object that reduces the list of available conversations using the specified criteria.
            focus_on_load: Indicates whether the element will be set to auto focus within the view object.
                Only one element can be set to true. Defaults to false.
        """
        super().__init__(
            type=self.type,
            action_id=action_id,
            placeholder=TextObject.parse(placeholder, PlainTextObject.type),
            confirm=ConfirmObject.parse(confirm),
            focus_on_load=focus_on_load,
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
        focus_on_load: Optional[bool] = None,
        **others: dict,
    ):
        """
        This select menu will populate its options with a list of public channels
        visible to the current user in the active workspace.
        https://api.slack.com/reference/block-kit/block-elements#channel_select

        Args:
            placeholder (required): A plain_text only text object that defines the placeholder text shown on the menu.
                Maximum length for the text in this field is 150 characters.
            action_id (required): An identifier for the action triggered when a menu option is selected.
                You can use this when you receive an interaction payload to identify the source of the action.
                Should be unique among all other action_ids in the containing block.
                Maximum length for this field is 255 characters.
            initial_channel: The ID of any valid public channel to be pre-selected when the menu loads.
            confirm: A confirm object that defines an optional confirmation dialog that appears
                after a menu item is selected.
            response_url_enabled: This field only works with menus in input blocks in modals.
                When set to true, the view_submission payload from the menu's parent view will contain a response_url.
                This response_url can be used for message responses.
                The target channel for the message will be determined by the value of this select menu
            focus_on_load: Indicates whether the element will be set to auto focus within the view object.
                Only one element can be set to true. Defaults to false.
        """
        super().__init__(
            type=self.type,
            action_id=action_id,
            placeholder=TextObject.parse(placeholder, PlainTextObject.type),
            confirm=ConfirmObject.parse(confirm),
            focus_on_load=focus_on_load,
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
        initial_channels: Optional[Sequence[str]] = None,
        confirm: Optional[Union[dict, ConfirmObject]] = None,
        max_selected_items: Optional[int] = None,
        focus_on_load: Optional[bool] = None,
        **others: dict,
    ):
        """
        This multi-select menu will populate its options with a list of public channels visible
        to the current user in the active workspace.
        https://api.slack.com/reference/block-kit/block-elements#channel_multi_select

        Args:
            placeholder (required): A plain_text only text object that defines the placeholder text shown on the menu.
                Maximum length for the text in this field is 150 characters.
            action_id (required): An identifier for the action triggered when a menu option is selected.
                You can use this when you receive an interaction payload to identify the source of the action.
                Should be unique among all other action_ids in the containing block.
                Maximum length for this field is 255 characters.
            initial_channels: An array of one or more IDs of any valid public channel
                to be pre-selected when the menu loads.
            confirm: A confirm object that defines an optional confirmation dialog that appears
                before the multi-select choices are submitted.
            max_selected_items: Specifies the maximum number of items that can be selected in the menu.
                Minimum number is 1.
            focus_on_load: Indicates whether the element will be set to auto focus within the view object.
                Only one element can be set to true. Defaults to false.
        """
        super().__init__(
            type=self.type,
            action_id=action_id,
            placeholder=TextObject.parse(placeholder, PlainTextObject.type),
            confirm=ConfirmObject.parse(confirm),
            focus_on_load=focus_on_load,
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
        initial_value: Optional[str] = None,
        multiline: Optional[bool] = None,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        dispatch_action_config: Optional[Union[dict, DispatchActionConfig]] = None,
        focus_on_load: Optional[bool] = None,
        **others: dict,
    ):
        """
        A plain-text input, similar to the HTML <input> tag, creates a field
        where a user can enter freeform data. It can appear as a single-line
        field or a larger textarea using the multiline flag. Plain-text input
        elements can be used inside of SectionBlocks and ActionsBlocks.
        https://api.slack.com/reference/block-kit/block-elements#input

        Args:
            action_id (required): An identifier for the input value when the parent modal is submitted.
                You can use this when you receive a view_submission payload to identify the value of the input element.
                Should be unique among all other action_ids in the containing block.
                Maximum length for this field is 255 characters.
            placeholder: A plain_text only text object that defines the placeholder text shown
                in the plain-text input. Maximum length for the text in this field is 150 characters.
            initial_value: The initial value in the plain-text input when it is loaded.
            multiline: Indicates whether the input will be a single line (false) or a larger textarea (true).
                Defaults to false.
            min_length: The minimum length of input that the user must provide. If the user provides less,
                they will receive an error. Maximum value is 3000.
            max_length: The maximum length of input that the user can provide. If the user provides more,
                they will receive an error.
            dispatch_action_config: A dispatch configuration object that determines when
                during text input the element returns a block_actions payload.
            focus_on_load: Indicates whether the element will be set to auto focus within the view object.
                Only one element can be set to true. Defaults to false.
        """
        super().__init__(
            type=self.type,
            action_id=action_id,
            placeholder=TextObject.parse(placeholder, PlainTextObject.type),
            focus_on_load=focus_on_load,
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
        options: Optional[Sequence[Union[dict, Option]]] = None,
        initial_option: Optional[Union[dict, Option]] = None,
        confirm: Optional[Union[dict, ConfirmObject]] = None,
        focus_on_load: Optional[bool] = None,
        **others: dict,
    ):
        """A radio button group that allows a user to choose one item from a list of possible options.
        https://api.slack.com/reference/block-kit/block-elements#radio

        Args:
            action_id (required): An identifier for the action triggered when the radio button group is changed.
                You can use this when you receive an interaction payload to identify the source of the action.
                Should be unique among all other action_ids in the containing block.
                Maximum length for this field is 255 characters.
            options (required): An array of option objects. A maximum of 10 options are allowed.
            initial_option: An option object that exactly matches one of the options.
                This option will be selected when the radio button group initially loads.
            confirm: A confirm object that defines an optional confirmation dialog that appears
                after clicking one of the radio buttons in this element.
            focus_on_load: Indicates whether the element will be set to auto focus within the view object.
                Only one element can be set to true. Defaults to false.
        """
        super().__init__(
            type=self.type,
            action_id=action_id,
            confirm=ConfirmObject.parse(confirm),
            focus_on_load=focus_on_load,
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
        options: Sequence[Union[Option]],
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

        Args:
            action_id (required): An identifier for the action triggered when a menu option is selected.
                You can use this when you receive an interaction payload to identify the source of the action.
                Should be unique among all other action_ids in the containing block.
                Maximum length for this field is 255 characters.
            options (required): An array of option objects to display in the menu.
                Maximum number of options is 5, minimum is 2.
            confirm: A confirm object that defines an optional confirmation dialog that appears
                after a menu item is selected.
        """
        super().__init__(action_id=action_id, type=self.type)
        show_unknown_key_warning(self, others)

        self.options = options
        self.confirm = ConfirmObject.parse(confirm)

    @JsonValidator(
        f"options attribute must have between {options_min_length} "
        f"and {options_max_length} items"
    )
    def _validate_options_length(self) -> bool:
        return self.options_min_length <= len(self.options) <= self.options_max_length
