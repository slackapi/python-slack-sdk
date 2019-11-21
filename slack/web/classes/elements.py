import random
import re
import string
from abc import ABCMeta, abstractmethod
from typing import List, Optional, Set, Union

from . import EnumValidator, JsonObject, JsonValidator, extract_json
from .objects import ButtonStyles, ConfirmObject, Option, OptionGroup, PlainTextObject


class BlockElement(JsonObject, metaclass=ABCMeta):
    def __init__(self, *, subtype: str):
        self.subtype = subtype

    def to_dict(self) -> dict:
        json = super().to_dict()
        json["type"] = self.subtype
        return json


class InteractiveElement(BlockElement):
    @property
    def attributes(self) -> Set[str]:
        return super().attributes.union({"action_id"})

    action_id_max_length = 255

    def __init__(self, *, action_id: str, subtype: str):
        super().__init__(subtype=subtype)
        self.action_id = action_id

    @JsonValidator(
        f"action_id attribute cannot exceed {action_id_max_length} characters"
    )
    def action_id_length(self):
        return len(self.action_id) <= self.action_id_max_length


class ImageElement(BlockElement):
    @property
    def attributes(self) -> Set[str]:
        return super().attributes.union({"alt_text", "image_url"})

    image_url_max_length = 3000
    alt_text_max_length = 2000

    def __init__(self, *, image_url: str, alt_text: str):
        """
        An element to insert an image - this element can be used in section and
        context blocks only. If you want a block with only an image in it,
        you're looking for the image block.

        https://api.slack.com/reference/messaging/block-elements#image

        Args:
            image_url: Publicly hosted URL to be displayed. Cannot exceed 3000
                characters.
            alt_text: Plain text summary of image. Cannot exceed 2000 characters.
        """
        super().__init__(subtype="image")
        self.image_url = image_url
        self.alt_text = alt_text

    @JsonValidator(
        f"image_url attribute cannot exceed {image_url_max_length} characters"
    )
    def image_url_length(self):
        return len(self.image_url) <= self.image_url_max_length

    @JsonValidator(f"alt_text attribute cannot exceed {alt_text_max_length} characters")
    def alt_text_length(self):
        return len(self.alt_text) <= self.alt_text_max_length


class ButtonElement(InteractiveElement):
    @property
    def attributes(self) -> Set[str]:
        return super().attributes.union({"style", "value"})

    text_max_length = 75
    value_max_length = 2000

    def __init__(
        self,
        *,
        text: str,
        action_id: str,
        value: str,
        style: Optional[str] = None,
        confirm: Optional[ConfirmObject] = None,
    ):
        """
        An interactive element that inserts a button. The button can be a trigger for
        anything from opening a simple link to starting a complex workflow.

        https://api.slack.com/reference/messaging/block-elements#button

        Args:
            text: String that defines the button's text. Cannot exceed 75 characters.
            action_id: ID to be used for this action - should be unique. Cannot
                exceed 255 characters.
            value: The value to send along with the interaction payload. Cannot
                exceed 2000 characters.
            style: "primary" or "danger" to add specific styling to this button.
            confirm: A ConfirmObject that defines an optional confirmation dialog
                after this element is interacted with.
        """
        super().__init__(action_id=action_id, subtype="button")
        self.text = text
        self.value = value
        self.style = style
        self.confirm = confirm

    @JsonValidator(f"text attribute cannot exceed {text_max_length} characters")
    def text_length(self):
        return len(self.text) <= self.text_max_length

    @JsonValidator(f"value attribute cannot exceed {value_max_length} characters")
    def value_length(self):
        return len(self.value) <= self.value_max_length

    @EnumValidator("style", ButtonStyles)
    def style_valid(self):
        return self.style is None or self.style in ButtonStyles

    def to_dict(self) -> dict:
        json = super().to_dict()
        json["text"] = PlainTextObject.direct_from_string(self.text)
        if self.confirm is not None:
            json["confirm"] = extract_json(self.confirm)
        return json


class LinkButtonElement(ButtonElement):
    @property
    def attributes(self) -> Set[str]:
        return super().attributes.union({"url"})

    url_max_length = 3000

    def __init__(self, *, text: str, url: str, style: Optional[str] = None):
        """
        A simple button that simply opens a given URL. You will still receive an
        interaction payload and will need to send an acknowledgement response.

        https://api.slack.com/reference/messaging/block-elements#button

        Args:
            text: String that defines the button's text. Cannot exceed 75 characters.
            url: A URL to load in the user's browser when the button is
                clicked. Maximum length for this field is 3000 characters.
            style: "primary" or "danger" to add specific styling to this button.
        """
        random_id = "".join(random.choice(string.ascii_uppercase) for _ in range(16))
        super().__init__(text=text, action_id=random_id, value="", style=style)
        self.url = url

    @JsonValidator(f"url attribute cannot exceed {url_max_length} characters")
    def url_length(self):
        return len(self.url) <= self.url_max_length

    def to_dict(self) -> dict:
        json = super().to_dict()
        # LinkButtonElements don't use the value property so we can just remove it
        if "value" in json:
            del json["value"]
        return json


class AbstractSelector(InteractiveElement, metaclass=ABCMeta):
    placeholder_max_length = 150

    def __init__(
        self,
        *,
        placeholder: str,
        action_id: str,
        subtype: str,
        confirm: Optional[ConfirmObject] = None,
    ):
        super().__init__(action_id=action_id, subtype=subtype)
        self.placeholder = placeholder
        self.confirm = confirm

    @JsonValidator(
        f"placeholder attribute cannot exceed {placeholder_max_length} characters"
    )
    def placeholder_length(self):
        return len(self.placeholder) <= self.placeholder_max_length

    def to_dict(self,) -> dict:
        json = super().to_dict()
        json["placeholder"] = PlainTextObject.direct_from_string(self.placeholder)
        if self.confirm is not None:
            json["confirm"] = extract_json(self.confirm)
        return json


class SelectElement(AbstractSelector):
    options_max_length = 100

    def __init__(
        self,
        *,
        placeholder: str,
        action_id: str,
        options: List[Union[Option, OptionGroup]],
        initial_option: Optional[Option] = None,
        confirm: Optional[ConfirmObject] = None,
    ):
        """
        This is the simplest form of select menu, with a static list of options
        passed in when defining the element.

        https://api.slack.com/reference/messaging/block-elements#static-select

        Args:
            placeholder: placeholder text shown on this element. Cannot exceed 150
                characters.
            action_id: ID to be used for this action - should be unique. Cannot
                exceed 255 characters.
            options: An array of Option or OptionGroup objects. Maximum number of
                options is 100.
            initial_option: A single option that exactly matches one of the
                options within options or option_groups. This option will be selected
                when the menu initially loads.
            confirm: A ConfirmObject that defines an optional confirmation dialog
                after this element is interacted with.
        """
        super().__init__(
            placeholder=placeholder,
            action_id=action_id,
            subtype="static_select",
            confirm=confirm,
        )
        self.options = options
        self.initial_option = initial_option

    @JsonValidator(f"options attribute cannot exceed {options_max_length} elements")
    def options_length(self):
        return len(self.options) <= self.options_max_length

    def to_dict(self) -> dict:
        json = super().to_dict()
        if isinstance(self.options[0], OptionGroup):
            json["option_groups"] = extract_json(self.options, "block")
        else:
            json["options"] = extract_json(self.options, "block")
        if self.initial_option is not None:
            json["initial_option"] = extract_json(self.initial_option, "block")
        return json


class ExternalDataSelectElement(AbstractSelector):
    @property
    def attributes(self) -> Set[str]:
        return super().attributes.union({"min_query_length"})

    def __init__(
        self,
        *,
        placeholder: str,
        action_id: str,
        initial_option: Union[Optional[Option], Optional[OptionGroup]] = None,
        min_query_length: Optional[int] = None,
        confirm: Optional[ConfirmObject] = None,
    ):
        """
        This select menu will load its options from an external data source, allowing
        for a dynamic list of options.

        https://api.slack.com/reference/messaging/block-elements#external-select

        Args:
            placeholder: placeholder text shown on this element. Cannot exceed 150
                characters.
            action_id: ID to be used for this action - should be unique. Cannot
                exceed 255 characters.
            initial_option: A single option that exactly matches one of the
                options within options or option_groups. This option will be selected
                when the menu initially loads.
            min_query_length: When the typeahead field is used, a request will be
                sent on every character change. If you prefer fewer requests or more
                fully ideated queries, use the min_query_length attribute to tell Slack
                the fewest number of typed characters required before dispatch.
            confirm: A ConfirmObject that defines an optional confirmation dialog
                after this element is interacted with.
        """
        super().__init__(
            action_id=action_id,
            subtype="external_select",
            placeholder=placeholder,
            confirm=confirm,
        )
        self.initial_option = initial_option
        self.min_query_length = min_query_length

    def to_dict(self) -> dict:
        json = super().to_dict()
        if self.initial_option is not None:
            json["initial_option"] = extract_json(self.initial_option, "block")
        return json


class AbstractDynamicSelector(AbstractSelector, metaclass=ABCMeta):
    @property
    @abstractmethod
    def initial_object_type(self):
        pass

    def __init__(
        self,
        *,
        placeholder: str,
        action_id: str,
        initial_value: Optional[str] = None,
        confirm: Optional[ConfirmObject] = None,
    ):
        super().__init__(
            action_id=action_id,
            subtype=f"{self.initial_object_type}s_select",
            confirm=confirm,
            placeholder=placeholder,
        )
        self.initial_value = initial_value

    def to_dict(self) -> dict:
        json = super().to_dict()
        if self.initial_value is not None:
            json[f"initial_{self.initial_object_type}"] = self.initial_value
        return json


class UserSelectElement(AbstractDynamicSelector):
    initial_object_type = "user"

    def __init__(
        self,
        *,
        placeholder: str,
        action_id: str,
        initial_user: Optional[str] = None,
        confirm: Optional[ConfirmObject] = None,
    ):
        """
        This select menu will populate its options with a list of Slack users visible to
        the current user in the active workspace.

        https://api.slack.com/reference/messaging/block-elements#users-select

        Args:
            placeholder: placeholder text shown on this element. Cannot exceed 150
                characters.
            action_id: ID to be used for this action - should be unique. Cannot
                exceed 255 characters.
            initial_user: An ID to initially select on this selector.
            confirm: A ConfirmObject that defines an optional confirmation dialog
                after this element is interacted with.
        """
        super().__init__(
            placeholder=placeholder,
            action_id=action_id,
            initial_value=initial_user,
            confirm=confirm,
        )


class ConversationSelectElement(AbstractDynamicSelector):
    initial_object_type = "conversation"

    def __init__(
        self,
        *,
        placeholder: str,
        action_id: str,
        initial_conversation: Optional[str] = None,
        confirm: Optional[ConfirmObject] = None,
    ):
        """
        This select menu will populate its options with a list of public and private
        channels, DMs, and MPIMs visible to the current user in the active workspace.

        https://api.slack.com/reference/messaging/block-elements#conversation-select

        Args:
            placeholder: placeholder text shown on this element. Cannot exceed 150
                characters.
            action_id: ID to be used for this action - should be unique. Cannot
                exceed 255 characters.
            initial_conversation: An ID to initially select on this selector.
            confirm: A ConfirmObject that defines an optional confirmation dialog
                after this element is interacted with.
        """
        super().__init__(
            placeholder=placeholder,
            action_id=action_id,
            initial_value=initial_conversation,
            confirm=confirm,
        )


class ChannelSelectElement(AbstractDynamicSelector):
    initial_object_type = "channel"

    def __init__(
        self,
        *,
        placeholder: str,
        action_id: str,
        initial_channel: Optional[str] = None,
        confirm: Optional[ConfirmObject] = None,
    ):
        """
        This select menu will populate its options with a list of public channels
        visible to the current user in the active workspace.

        https://api.slack.com/reference/messaging/block-elements#channel-select

        Args:
            placeholder: placeholder text shown on this element. Cannot exceed 150
                characters.
            action_id: ID to be used for this action - should be unique. Cannot
                exceed 255 characters.
            initial_channel: An ID to initially select on this selector.
            confirm: A ConfirmObject that defines an optional confirmation dialog
                after this element is interacted with.
        """
        super().__init__(
            placeholder=placeholder,
            action_id=action_id,
            initial_value=initial_channel,
            confirm=confirm,
        )


class OverflowMenuOption(Option):
    def __init__(self, label: str, value: str, url: Optional[str] = None):
        """
        An extension of a standard option, but with an optional 'url' attribute,
        which will simply directly navigate to a given URL. Only valid in
        OverflowMenuElements, as the name implies.

        https://api.slack.com/reference/messaging/composition-objects#option

        Args:
              label: A short, user-facing string to label this option to users.
                Cannot exceed 75 characters.
            value: A short string that identifies this particular option to your
                application. It will be part of the payload when this option is
                selected. Cannot exceed 75 characters.
            url: A URL to load in the user's browser when the option is clicked.
                Maximum length for this field is 3000 characters. If you're using url,
                you'll still receive an interaction payload and will need to send an
                acknowledgement response.
        """
        super().__init__(label=label, value=value)
        self.url = url

    def to_dict(self, option_type: str = "block") -> dict:
        json = super().to_dict(option_type)
        if self.url is not None:
            json["url"] = self.url
        return json


class OverflowMenuElement(InteractiveElement):
    options_min_length = 2
    options_max_length = 5

    def __init__(
        self,
        *,
        options: List[Union[Option, OverflowMenuOption]],
        action_id: str,
        confirm: Optional[ConfirmObject] = None,
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

        https://api.slack.com/reference/messaging/block-elements#overflow

        Args:
            options: An array of Option or OverflowMenuOption objects to display
                in the menu. Maximum number of options is 5, minimum is 2.
            action_id: ID to be used for this action - should be unique. Cannot
                exceed 255 characters.
            confirm: A ConfirmObject that defines an optional confirmation dialog
                after this element is interacted with.
        """
        super().__init__(action_id=action_id, subtype="overflow")
        self.options = options
        self.confirm = confirm

    @JsonValidator(
        f"options attribute must have between {options_min_length} "
        f"and {options_max_length} items"
    )
    def options_length(self):
        return self.options_min_length < len(self.options) <= self.options_max_length

    def to_dict(self) -> dict:
        json = super().to_dict()
        json["options"] = extract_json(self.options, "block")
        if self.confirm is not None:
            json["confirm"] = extract_json(self.confirm)
        return json


class DatePickerElement(AbstractSelector):
    @property
    def attributes(self) -> Set[str]:
        return super().attributes.union({"initial_date"})

    def __init__(
        self,
        *,
        action_id: str,
        placeholder: Optional[str] = None,
        initial_date: Optional[str] = None,
        confirm: Optional[ConfirmObject] = None,
    ):
        """
        An element which lets users easily select a date from a calendar style UI.
        Date picker elements can be used inside of SectionBlocks and ActionsBlocks.

        https://api.slack.com/reference/messaging/block-elements#datepicker

        Args:
            action_id: ID to be used for this action - should be unique. Cannot
                exceed 255 characters.
            placeholder: placeholder text shown on this element. Cannot exceed 150
                characters.
            initial_date: The initial date that is selected when the element is
                loaded. This must be in the format "YYYY-MM-DD".
            confirm: A ConfirmObject that defines an optional confirmation dialog
                after this element is interacted with.
        """
        super().__init__(
            action_id=action_id,
            subtype="datepicker",
            placeholder=placeholder,
            confirm=confirm,
        )
        self.initial_date = initial_date

    @JsonValidator("initial_date attribute must be in format 'YYYY-MM-DD'")
    def initial_date_valid(self):
        return self.initial_date is None or re.match(
            r"\d{4}-[01][12]-[0123]\d", self.initial_date
        )
