import random
import re
import string
from abc import ABCMeta, abstractmethod
from typing import List, Set, Union

from .objects import (
    ButtonStyles,
    ConfirmObject,
    EnumValidator,
    JsonObject,
    JsonValidator,
    OptionGroupObject,
    OptionObject,
    OptionTypes,
    PlainTextObject,
    extract_json,
)


class BlockElement(JsonObject):
    attributes = {"type"}

    def __init__(self, *, type: str):
        self.type = type


class InteractiveElement(BlockElement):
    @property
    def attributes(self) -> Set[str]:
        return super().attributes.union({"action_id"})

    def __init__(self, *, action_id: str, type: str):
        super().__init__(type=type)
        self.action_id = action_id

    @JsonValidator("action_id attribute cannot exceed 255 characters")
    def action_id_length(self):
        return len(self.action_id) <= 255


class ImageElement(BlockElement):
    @property
    def attributes(self) -> Set[str]:
        return super().attributes.union({"image_url", "alt_text"})

    def __init__(self, *, image_url: str, alt_text: str):
        """
        An element to insert an image - this element can be used in section and
        context blocks only. If you want a block with only an image in it,
        you're looking for the image block.

        https://api.slack.com/reference/messaging/block-elements#image

        :param image_url: Publicly hosted URL to be displayed. Cannot exceed 3000
            characters.

        :param alt_text: Plain text summary of image. Cannot exceed 2000 characters.
        """
        super().__init__(type="image")
        self.image_url = image_url
        self.alt_text = alt_text

    @JsonValidator("image_url attribute cannot exceed 3000 characters")
    def image_url_length(self):
        return len(self.image_url) <= 3000

    @JsonValidator("alt_text attribute cannot exceed 2000 characters")
    def alt_text_length(self):
        return len(self.alt_text) <= 2000


class ButtonElement(InteractiveElement):
    @property
    def attributes(self) -> Set[str]:
        return super().attributes.union({"value", "style"})

    def __init__(
        self,
        *,
        text: str,
        action_id: str,
        value: str,
        style: str = None,
        confirm: ConfirmObject = None,
    ):
        """
        An interactive element that inserts a button. The button can be a trigger for
        anything from opening a simple link to starting a complex workflow.

        https://api.slack.com/reference/messaging/block-elements#button

        :param text: String that defines the button's text. Cannot exceed 75 characters.

        :param action_id: ID to be used for this action - should be unique. Cannot
            exceed 255 characters.

        :param value: The value to send along with the interaction payload. Cannot
            exceed 2000 characters.

        :param style: "primary" or "danger" to add specific styling to this button.

        :param confirm: A ConfirmObject that defines an optional confirmation dialog
            after this element is interacted with.
        """
        super().__init__(action_id=action_id, type="button")
        self.text = text
        self.value = value
        self.style = style
        self.confirm = confirm

    @JsonValidator("text attribute cannot exceed 75 characters")
    def text_length(self):
        return len(self.text) <= 75

    @JsonValidator("value attribute cannot exceed 75 characters")
    def value_length(self):
        return len(self.value) <= 75

    @EnumValidator("style", ButtonStyles)
    def style_valid(self):
        return self.style is None or self.style in ButtonStyles

    def get_json(self) -> dict:
        json = super().get_json()
        json["text"] = PlainTextObject.from_string(self.text)
        if self.confirm is not None:
            json["confirm"] = extract_json(self.confirm, ConfirmObject)
        return json


class LinkButtonElement(ButtonElement):
    @property
    def attributes(self) -> Set[str]:
        return super().attributes.union({"url"})

    def __init__(self, *, text: str, url: str, style: str = None):
        """
        A simple button that simply opens a given URL. You will still receive an
        interaction payload and will need to send an acknowledgement response.

        https://api.slack.com/reference/messaging/block-elements#button

        :param text: String that defines the button's text. Cannot exceed 75 characters.

        :param url: A URL to load in the user's browser when the button is
            clicked. Maximum length for this field is 3000 characters.

        :param style: "primary" or "danger" to add specific styling to this button.
        """
        random_id = "".join(random.choice(string.ascii_uppercase) for _ in range(16))
        super().__init__(text=text, action_id=random_id, value="", style=style)
        self.url = url

    @JsonValidator("url attribute cannot exceed 3000 characters")
    def url_length(self):
        return len(self.url) <= 3000


class AbstractSelector(InteractiveElement, metaclass=ABCMeta):
    def __init__(
        self,
        *,
        placeholder: str,
        action_id: str,
        type: str,
        confirm: ConfirmObject = None,
    ):
        super().__init__(action_id=action_id, type=type)
        self.placeholder = placeholder
        self.confirm = confirm

    @JsonValidator("placeholder attribute cannot exceed 150 characters")
    def placeholder_length(self):
        return len(self.placeholder) <= 150

    def get_json(self,) -> dict:
        json = super().get_json()
        json["placeholder"] = PlainTextObject.from_string(self.placeholder)
        if self.confirm is not None:
            json["confirm"] = extract_json(self.confirm, ConfirmObject)
        return json


class SelectElement(AbstractSelector):
    def __init__(
        self,
        *,
        placeholder: str,
        action_id: str,
        options: List[Union[OptionObject, OptionGroupObject]],
        initial_option: OptionObject = None,
        confirm: ConfirmObject = None,
    ):
        """
        This is the simplest form of select menu, with a static list of options
        passed in when defining the element.

        https://api.slack.com/reference/messaging/block-elements#static-select

        :param placeholder: placeholder text shown on this element. Cannot exceed 150
            characters.

        :param action_id: ID to be used for this action - should be unique. Cannot
            exceed 255 characters.

        :param options: An array of Option or OptionGroup objects. Maximum number of
            options is 100.

        :param initial_option: A single option that exactly matches one of the
            options within options or option_groups. This option will be selected when
            the menu initially loads.

        :param confirm: A ConfirmObject that defines an optional confirmation dialog
            after this element is interacted with.
        """
        super().__init__(
            placeholder=placeholder,
            action_id=action_id,
            type="static_select",
            confirm=confirm,
        )
        self.options = options
        self.initial_option = initial_option

    @JsonValidator("options attribute cannot exceed 100 items")
    def options_length(self):
        return len(self.options) <= 100

    def get_json(self) -> dict:
        json = super().get_json()
        if isinstance(self.options[0], OptionObject):
            json["options"] = extract_json(self.options, OptionTypes, "block")
        else:
            json["option_groups"] = extract_json(self.options, OptionTypes, "block")
        if self.initial_option is not None:
            json["initial_option"] = extract_json(
                self.initial_option, OptionTypes, "block"
            )
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
        initial_option: OptionTypes = None,
        min_query_length: int = None,
        confirm: ConfirmObject = None,
    ):
        """
        This select menu will load its options from an external data source, allowing
        for a dynamic list of options.

        https://api.slack.com/reference/messaging/block-elements#external-select

        :param placeholder: placeholder text shown on this element. Cannot exceed 150
            characters.

        :param action_id: ID to be used for this action - should be unique. Cannot
            exceed 255 characters.

        :param initial_option: A single option that exactly matches one of the
            options within options or option_groups. This option will be selected when
            the menu initially loads.

        :param min_query_length: When the typeahead field is used, a request will be
            sent on every character change. If you prefer fewer requests or more fully
            ideated queries, use the min_query_length attribute to tell Slack the fewest
            number of typed characters required before dispatch.

        :param confirm: A ConfirmObject that defines an optional confirmation dialog
            after this element is interacted with.
        """
        super().__init__(
            action_id=action_id,
            type="external_select",
            placeholder=placeholder,
            confirm=confirm,
        )
        self.initial_option = initial_option
        self.min_query_length = min_query_length

    def get_json(self) -> dict:
        json = super().get_json()
        if self.initial_option is not None:
            json["initial_option"] = extract_json(
                self.initial_option, OptionTypes, "block"
            )
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
        initial_value: str = None,
        confirm: ConfirmObject = None,
    ):
        """
        This select menu will populate its options automatically a list of the
        appropriate type that is visible to the current user in the active workspace.

        https://api.slack.com/reference/messaging/block-elements#users-select

        https://api.slack.com/reference/messaging/block-elements#conversation-select

        https://api.slack.com/reference/messaging/block-elements#channel-select

        :param placeholder: placeholder text shown on this element. Cannot exceed 150
            characters.

        :param action_id: ID to be used for this action - should be unique. Cannot
            exceed 255 characters.

        :param initial_value: An ID to initially select on this selector.

        :param confirm: A ConfirmObject that defines an optional confirmation dialog
            after this element is interacted with.
        """
        super().__init__(
            action_id=action_id,
            type=f"{self.initial_object_type}s_select",
            confirm=confirm,
            placeholder=placeholder,
        )
        self.initial_value = initial_value

    def get_json(self) -> dict:
        json = super().get_json()
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
        initial_value: str = None,
        confirm: ConfirmObject = None,
    ):
        """
        This select menu will populate its options with a list of Slack users visible to
        the current user in the active workspace.

        https://api.slack.com/reference/messaging/block-elements#users-select

        :param placeholder: placeholder text shown on this element. Cannot exceed 150
            characters.

        :param action_id: ID to be used for this action - should be unique. Cannot
            exceed 255 characters.

        :param initial_value: An ID to initially select on this selector.

        :param confirm: A ConfirmObject that defines an optional confirmation dialog
            after this element is interacted with.
        """
        super().__init__(
            placeholder=placeholder,
            action_id=action_id,
            initial_value=initial_value,
            confirm=confirm,
        )


class ConversationSelectElement(AbstractDynamicSelector):
    initial_object_type = "conversation"

    def __init__(
        self,
        *,
        placeholder: str,
        action_id: str,
        initial_value: str = None,
        confirm: ConfirmObject = None,
    ):
        """
        This select menu will populate its options with a list of public and private
        channels, DMs, and MPIMs visible to the current user in the active workspace.

        https://api.slack.com/reference/messaging/block-elements#conversation-select

        :param placeholder: placeholder text shown on this element. Cannot exceed 150
            characters.

        :param action_id: ID to be used for this action - should be unique. Cannot
            exceed 255 characters.

        :param initial_value: An ID to initially select on this selector.

        :param confirm: A ConfirmObject that defines an optional confirmation dialog
            after this element is interacted with.
        """
        super().__init__(
            placeholder=placeholder,
            action_id=action_id,
            initial_value=initial_value,
            confirm=confirm,
        )


class ChannelSelectElement(AbstractDynamicSelector):
    initial_object_type = "channel"

    def __init__(
        self,
        *,
        placeholder: str,
        action_id: str,
        initial_value: str = None,
        confirm: ConfirmObject = None,
    ):
        """
        This select menu will populate its options with a list of public channels visible
        to the current user in the active workspace.

        https://api.slack.com/reference/messaging/block-elements#channel-select

        :param placeholder: placeholder text shown on this element. Cannot exceed 150
            characters.

        :param action_id: ID to be used for this action - should be unique. Cannot
            exceed 255 characters.

        :param initial_value: An ID to initially select on this selector.

        :param confirm: A ConfirmObject that defines an optional confirmation dialog
            after this element is interacted with.
        """
        super().__init__(
            placeholder=placeholder,
            action_id=action_id,
            initial_value=initial_value,
            confirm=confirm,
        )


class OverflowMenuOption(OptionObject):
    def __init__(self, label: str, value: str, url: str = None):
        """
        An extension of a standard option, but with an optional 'url' attribute, which will simply directly navigate to a given URL.

        https://api.slack.com/reference/messaging/composition-objects#option

        :param label: A short, user-facing string to label this option to users.
            Cannot exceed 75 characters.

        :param value: A short string that identifies this particular option to your
            application. It will be part of the payload when this option is selected.
            Cannot exceed 75 characters.

        :param url: A URL to load in the user's browser when the option is clicked.
            Maximum length for this field is 3000 characters. If you're using url,
            you'll still receive an interaction payload and will need to send an
            acknowledgement response.
        """
        super().__init__(label=label, value=value)
        self.url = url

    def get_json(self, option_type: str = "block") -> dict:
        json = super().get_json(option_type)
        if self.url is not None:
            json["url"] = self.url
        return json


class OverflowMenuElement(InteractiveElement):
    def __init__(
        self,
        *,
        options: List[Union[OptionObject, OverflowMenuOption]],
        action_id: str,
        confirm: ConfirmObject = None,
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

        :param options: An array of Option or OverflowMenuOption objects to display
            in the menu. Maximum number of options is 5, minimum is 2.

        :param action_id: ID to be used for this action - should be unique. Cannot
            exceed 255 characters.

        :param confirm: A ConfirmObject that defines an optional confirmation dialog
            after this element is interacted with.
        """
        super().__init__(action_id=action_id, type="overflow")
        self.options = options
        self.confirm = confirm

    @JsonValidator("options attribute must have between 2 and 5 items")
    def options_length(self):
        return 2 < len(self.options) <= 5

    def get_json(self) -> dict:
        json = super().get_json()
        json["options"] = extract_json(self.options, OptionObject, "block")
        if self.confirm is not None:
            json["confirm"] = extract_json(self.confirm, ConfirmObject)
        return json


class DatePickerElement(AbstractSelector):
    @property
    def attributes(self) -> Set[str]:
        return super().attributes.union({"initial_date"})

    def __init__(
        self,
        *,
        action_id: str,
        placeholder: str = None,
        initial_date: str = None,
        confirm: ConfirmObject = None,
    ):
        """
        An element which lets users easily select a date from a calendar style UI.
        Date picker elements can be used inside of SectionBlocks and ActionsBlocks.

        https://api.slack.com/reference/messaging/block-elements#datepicker

        :param action_id: ID to be used for this action - should be unique. Cannot
            exceed 255 characters.

        :param placeholder: placeholder text shown on this element. Cannot exceed 150
            characters.

        :param initial_date: The initial date that is selected when the element is
            loaded. This must be in the format YYYY-MM-DD.

        :param confirm: A ConfirmObject that defines an optional confirmation dialog
            after this element is interacted with.
        """
        super().__init__(
            action_id=action_id,
            type="datepicker",
            placeholder=placeholder,
            confirm=confirm,
        )
        self.initial_date = initial_date

    @JsonValidator("initial_date attribute must be in format 'YYYY-MM-DD'")
    def initial_date_valid(self):
        return self.initial_date is None or re.match(
            r"\d{4}-[01][12]-[0123]\d", self.initial_date
        )
