import unittest

from slack.errors import SlackObjectFormationError
from slack.web.classes.elements import (
    ButtonElement,
    DatePickerElement,
    ExternalDataSelectElement,
    ImageElement,
    LinkButtonElement,
    UserSelectElement,
    StaticSelectElement,
    CheckboxesElement,
    StaticMultiSelectElement,
    ExternalDataMultiSelectElement,
    UserMultiSelectElement,
    ConversationMultiSelectElement,
    ChannelMultiSelectElement,
    OverflowMenuElement,
    PlainTextInputElement,
    RadioButtonsElement,
    ConversationSelectElement,
    ChannelSelectElement,
)
from slack.web.classes.objects import ConfirmObject, Option
from . import STRING_3001_CHARS, STRING_301_CHARS


# -------------------------------------------------
# Interactive Elements
# -------------------------------------------------


class InteractiveElementTests(unittest.TestCase):
    def test_action_id(self):
        with self.assertRaises(SlackObjectFormationError):
            ButtonElement(text="click me!", action_id=STRING_301_CHARS, value="clickable button").to_dict()


class ButtonElementTests(unittest.TestCase):
    def test_document_1(self):
        input = {
            "type": "button",
            "text": {"type": "plain_text", "text": "Click Me"},
            "value": "click_me_123",
            "action_id": "button",
        }
        self.assertDictEqual(input, ButtonElement(**input).to_dict())

    def test_document_2(self):
        input = {
            "type": "button",
            "text": {"type": "plain_text", "text": "Save"},
            "style": "primary",
            "value": "click_me_123",
            "action_id": "button",
        }
        self.assertDictEqual(input, ButtonElement(**input).to_dict())

    def test_document_3(self):
        input = {
            "type": "button",
            "text": {"type": "plain_text", "text": "Link Button"},
            "url": "https://docs.slack.dev/block-kit/",
        }
        self.assertDictEqual(input, ButtonElement(**input).to_dict())
        self.assertDictEqual(input, LinkButtonElement(**input).to_dict())

    def test_json(self):
        self.assertDictEqual(
            {
                "text": {"emoji": True, "text": "button text", "type": "plain_text"},
                "action_id": "some_button",
                "value": "button_123",
                "type": "button",
            },
            ButtonElement(text="button text", action_id="some_button", value="button_123").to_dict(),
        )

        confirm = ConfirmObject(title="really?", text="are you sure?")
        self.assertDictEqual(
            {
                "text": {"emoji": True, "text": "button text", "type": "plain_text"},
                "action_id": "some_button",
                "value": "button_123",
                "type": "button",
                "style": "primary",
                "confirm": confirm.to_dict(),
            },
            ButtonElement(
                text="button text",
                action_id="some_button",
                value="button_123",
                style="primary",
                confirm=confirm,
            ).to_dict(),
        )

    def test_text_length(self):
        with self.assertRaises(SlackObjectFormationError):
            ButtonElement(text=STRING_301_CHARS, action_id="button", value="click_me").to_dict()

    def test_value_length(self):
        with self.assertRaises(SlackObjectFormationError):
            ButtonElement(text="Button", action_id="button", value=STRING_3001_CHARS).to_dict()

    def test_invalid_style(self):
        with self.assertRaises(SlackObjectFormationError):
            ButtonElement(text="Button", action_id="button", value="button", style="invalid").to_dict()


class LinkButtonElementTests(unittest.TestCase):
    def test_json(self):
        button = LinkButtonElement(action_id="test", text="button text", url="http://google.com")
        self.assertDictEqual(
            {
                "text": {"emoji": True, "text": "button text", "type": "plain_text"},
                "url": "http://google.com",
                "type": "button",
                "action_id": button.action_id,
            },
            button.to_dict(),
        )

    def test_url_length(self):
        with self.assertRaises(SlackObjectFormationError):
            LinkButtonElement(text="Button", url=STRING_3001_CHARS).to_dict()


# -------------------------------------------------
# Checkboxes
# -------------------------------------------------


class CheckboxesElementTests(unittest.TestCase):
    def test_document(self):
        input = {
            "type": "checkboxes",
            "action_id": "this_is_an_action_id",
            "initial_options": [{"value": "A1", "text": {"type": "plain_text", "text": "Checkbox 1"}}],
            "options": [
                {"value": "A1", "text": {"type": "plain_text", "text": "Checkbox 1"}},
                {"value": "A2", "text": {"type": "plain_text", "text": "Checkbox 2"}},
            ],
        }
        self.assertDictEqual(input, CheckboxesElement(**input).to_dict())


# -------------------------------------------------
# DatePicker
# -------------------------------------------------


class DatePickerElementTests(unittest.TestCase):
    def test_document(self):
        input = {
            "type": "datepicker",
            "action_id": "datepicker123",
            "initial_date": "1990-04-28",
            "placeholder": {"type": "plain_text", "text": "Select a date"},
            "confirm": {
                "title": {"type": "plain_text", "text": "Are you sure?"},
                "text": {
                    "type": "mrkdwn",
                    "text": "Wouldn't you prefer a good game of _chess_?",
                },
                "confirm": {"type": "plain_text", "text": "Do it"},
                "deny": {"type": "plain_text", "text": "Stop, I've changed my mind!"},
            },
        }
        self.assertDictEqual(input, DatePickerElement(**input).to_dict())

    def test_json(self):
        for month in range(1, 12):
            for day in range(1, 31):
                date = f"2020-{month:02}-{day:02}"
                self.assertDictEqual(
                    {
                        "action_id": "datepicker-action",
                        "initial_date": date,
                        "placeholder": {
                            "emoji": True,
                            "text": "Select a date",
                            "type": "plain_text",
                        },
                        "type": "datepicker",
                    },
                    DatePickerElement(
                        action_id="datepicker-action",
                        placeholder="Select a date",
                        initial_date=date,
                    ).to_dict(),
                )

    def test_issue_623(self):
        elem = DatePickerElement(action_id="1", placeholder=None)
        elem.to_dict()  # no exception
        elem = DatePickerElement(action_id="1")
        elem.to_dict()  # no exception
        with self.assertRaises(SlackObjectFormationError):
            elem = DatePickerElement(action_id="1", placeholder="12345" * 100)
            elem.to_dict()


# -------------------------------------------------
# Image
# -------------------------------------------------


class ImageElementTests(unittest.TestCase):
    def test_document(self):
        input = {
            "type": "image",
            "image_url": "http://placekitten.com/700/500",
            "alt_text": "Multiple cute kittens",
        }
        self.assertDictEqual(input, ImageElement(**input).to_dict())

    def test_json(self):
        self.assertDictEqual(
            {
                "image_url": "http://google.com",
                "alt_text": "not really an image",
                "type": "image",
            },
            ImageElement(image_url="http://google.com", alt_text="not really an image").to_dict(),
        )

    def test_image_url_length(self):
        with self.assertRaises(SlackObjectFormationError):
            ImageElement(image_url=STRING_3001_CHARS, alt_text="text").to_dict()

    def test_alt_text_length(self):
        with self.assertRaises(SlackObjectFormationError):
            ImageElement(image_url="http://google.com", alt_text=STRING_3001_CHARS).to_dict()


# -------------------------------------------------
# Static Select
# -------------------------------------------------


class StaticMultiSelectElementTests(unittest.TestCase):
    maxDiff = None

    def test_document(self):
        input = {
            "action_id": "text1234",
            "type": "multi_static_select",
            "placeholder": {"type": "plain_text", "text": "Select items"},
            "options": [
                {
                    "text": {"type": "plain_text", "text": "*this is plain_text text*"},
                    "value": "value-0",
                },
                {
                    "text": {"type": "plain_text", "text": "*this is plain_text text*"},
                    "value": "value-1",
                },
                {
                    "text": {"type": "plain_text", "text": "*this is plain_text text*"},
                    "value": "value-2",
                },
            ],
            "max_selected_items": 1,
        }
        self.assertDictEqual(input, StaticMultiSelectElement(**input).to_dict())


class StaticSelectElementTests(unittest.TestCase):
    maxDiff = None

    def test_document_options(self):
        input = {
            "action_id": "text1234",
            "type": "static_select",
            "placeholder": {"type": "plain_text", "text": "Select an item"},
            "options": [
                {
                    "text": {"type": "plain_text", "text": "*this is plain_text text*"},
                    "value": "value-0",
                },
                {
                    "text": {"type": "plain_text", "text": "*this is plain_text text*"},
                    "value": "value-1",
                },
                {
                    "text": {"type": "plain_text", "text": "*this is plain_text text*"},
                    "value": "value-2",
                },
            ],
        }
        self.assertDictEqual(input, StaticSelectElement(**input).to_dict())

    def test_document_option_groups(self):
        input = {
            "action_id": "text1234",
            "type": "static_select",
            "placeholder": {"type": "plain_text", "text": "Select an item"},
            "option_groups": [
                {
                    "label": {"type": "plain_text", "text": "Group 1"},
                    "options": [
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "*this is plain_text text*",
                            },
                            "value": "value-0",
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "*this is plain_text text*",
                            },
                            "value": "value-1",
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "*this is plain_text text*",
                            },
                            "value": "value-2",
                        },
                    ],
                },
                {
                    "label": {"type": "plain_text", "text": "Group 2"},
                    "options": [
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "*this is plain_text text*",
                            },
                            "value": "value-3",
                        }
                    ],
                },
            ],
        }
        self.assertDictEqual(input, StaticSelectElement(**input).to_dict())

    option_one = Option.from_single_value("one")
    option_two = Option.from_single_value("two")
    options = [option_one, option_two, Option.from_single_value("three")]

    def test_json(self):
        dict_options = []
        for o in self.options:
            dict_options.append(o.to_dict())

        self.assertDictEqual(
            {
                "placeholder": {
                    "emoji": True,
                    "text": "selectedValue",
                    "type": "plain_text",
                },
                "action_id": "dropdown",
                "options": dict_options,
                "initial_option": self.option_two.to_dict(),
                "type": "static_select",
            },
            StaticSelectElement(
                placeholder="selectedValue",
                action_id="dropdown",
                options=self.options,
                initial_option=self.option_two,
            ).to_dict(),
        )

        self.assertDictEqual(
            {
                "placeholder": {
                    "emoji": True,
                    "text": "selectedValue",
                    "type": "plain_text",
                },
                "action_id": "dropdown",
                "options": dict_options,
                "confirm": ConfirmObject(title="title", text="text").to_dict("block"),
                "type": "static_select",
            },
            StaticSelectElement(
                placeholder="selectedValue",
                action_id="dropdown",
                options=self.options,
                confirm=ConfirmObject(title="title", text="text"),
            ).to_dict(),
        )

    def test_options_length(self):
        with self.assertRaises(SlackObjectFormationError):
            StaticSelectElement(
                placeholder="select",
                action_id="selector",
                options=[self.option_one] * 101,
            ).to_dict()


# -------------------------------------------------
# External Data Source Select
# -------------------------------------------------


class ExternalDataMultiSelectElementTests(unittest.TestCase):
    maxDiff = None

    def test_document(self):
        input = {
            "action_id": "text1234",
            "type": "multi_external_select",
            "placeholder": {"type": "plain_text", "text": "Select items"},
            "min_query_length": 3,
        }
        self.assertDictEqual(input, ExternalDataMultiSelectElement(**input).to_dict())

    def test_document_initial_options(self):
        input = {
            "action_id": "text1234",
            "type": "multi_external_select",
            "placeholder": {"type": "plain_text", "text": "Select items"},
            "initial_options": [
                {
                    "text": {"type": "plain_text", "text": "The default channel"},
                    "value": "C1234567890",
                }
            ],
            "min_query_length": 0,
            "max_selected_items": 1,
        }
        self.assertDictEqual(input, ExternalDataMultiSelectElement(**input).to_dict())


class ExternalDataSelectElementTests(unittest.TestCase):
    maxDiff = None

    def test_document_1(self):
        input = {
            "action_id": "text1234",
            "type": "external_select",
            "placeholder": {"type": "plain_text", "text": "Select an item"},
            "min_query_length": 3,
        }
        self.assertDictEqual(input, ExternalDataSelectElement(**input).to_dict())

    def test_document_2(self):
        input = {
            "action_id": "text1234",
            "type": "external_select",
            "placeholder": {"type": "plain_text", "text": "Select an item"},
            "initial_option": {
                "text": {"type": "plain_text", "text": "The default channel"},
                "value": "C1234567890",
            },
            "confirm": {
                "title": {"type": "plain_text", "text": "Are you sure?"},
                "text": {
                    "type": "mrkdwn",
                    "text": "Wouldn't you prefer a good game of _chess_?",
                },
                "confirm": {"type": "plain_text", "text": "Do it"},
                "deny": {"type": "plain_text", "text": "Stop, I've changed my mind!"},
            },
            "min_query_length": 3,
        }
        self.assertDictEqual(input, ExternalDataSelectElement(**input).to_dict())

    def test_json(self):
        self.assertDictEqual(
            {
                "placeholder": {
                    "emoji": True,
                    "text": "selectedValue",
                    "type": "plain_text",
                },
                "action_id": "dropdown",
                "min_query_length": 5,
                "type": "external_select",
            },
            ExternalDataSelectElement(placeholder="selectedValue", action_id="dropdown", min_query_length=5).to_dict(),
        )
        self.assertDictEqual(
            {
                "placeholder": {
                    "emoji": True,
                    "text": "selectedValue",
                    "type": "plain_text",
                },
                "action_id": "dropdown",
                "confirm": ConfirmObject(title="title", text="text").to_dict("block"),
                "type": "external_select",
            },
            ExternalDataSelectElement(
                placeholder="selectedValue",
                action_id="dropdown",
                confirm=ConfirmObject(title="title", text="text"),
            ).to_dict(),
        )


# -------------------------------------------------
# Users Select
# -------------------------------------------------


class UserSelectMultiElementTests(unittest.TestCase):
    def test_document(self):
        input = {
            "action_id": "text1234",
            "type": "multi_users_select",
            "placeholder": {"type": "plain_text", "text": "Select users"},
            "initial_users": ["U123", "U234"],
            "max_selected_items": 1,
        }
        self.assertDictEqual(input, UserMultiSelectElement(**input).to_dict())


class UserSelectElementTests(unittest.TestCase):
    def test_document(self):
        input = {
            "action_id": "text1234",
            "type": "users_select",
            "placeholder": {"type": "plain_text", "text": "Select an item"},
            "initial_user": "U123",
        }
        self.assertDictEqual(input, UserSelectElement(**input).to_dict())

    def test_json(self):
        self.assertDictEqual(
            {
                "action_id": "a-123",
                "type": "users_select",
                "initial_user": "U123",
                "placeholder": {
                    "type": "plain_text",
                    "text": "abc",
                    "emoji": True,
                },
            },
            UserSelectElement(
                placeholder="abc",
                action_id="a-123",
                initial_user="U123",
            ).to_dict(),
        )


# -------------------------------------------------
# Conversations Select
# -------------------------------------------------


class ConversationSelectMultiElementTests(unittest.TestCase):
    def test_document(self):
        input = {
            "action_id": "text1234",
            "type": "multi_conversations_select",
            "placeholder": {"type": "plain_text", "text": "Select conversations"},
            "initial_conversations": ["C123", "C234"],
            "max_selected_items": 2,
            "default_to_current_conversation": True,
            "filter": {"include": ["public", "mpim"], "exclude_bot_users": True},
        }
        self.assertDictEqual(input, ConversationMultiSelectElement(**input).to_dict())


class ConversationSelectElementTests(unittest.TestCase):
    def test_document(self):
        input = {
            "action_id": "text1234",
            "type": "conversations_select",
            "placeholder": {"type": "plain_text", "text": "Select an item"},
            "initial_conversation": "C123",
            "response_url_enabled": True,
            "default_to_current_conversation": True,
            "filter": {"include": ["public", "mpim"], "exclude_bot_users": True},
        }
        self.assertDictEqual(input, ConversationSelectElement(**input).to_dict())


# -------------------------------------------------
# Channels Select
# -------------------------------------------------


class ChannelSelectMultiElementTests(unittest.TestCase):
    def test_document(self):
        input = {
            "action_id": "text1234",
            "type": "multi_channels_select",
            "placeholder": {"type": "plain_text", "text": "Select channels"},
            "initial_channels": ["C123", "C234"],
            "max_selected_items": 2,
        }
        self.assertDictEqual(input, ChannelMultiSelectElement(**input).to_dict())


class ChannelSelectElementTests(unittest.TestCase):
    def test_document(self):
        input = {
            "action_id": "text1234",
            "type": "channels_select",
            "placeholder": {"type": "plain_text", "text": "Select an item"},
            "response_url_enabled": True,
            "initial_channel": "C123",
        }
        self.assertDictEqual(input, ChannelSelectElement(**input).to_dict())


# -------------------------------------------------
# Overflow Menu Select
# -------------------------------------------------


class OverflowMenuElementTests(unittest.TestCase):
    def test_document(self):
        input = {
            "type": "overflow",
            "options": [
                {
                    "text": {"type": "plain_text", "text": "*this is plain_text text*"},
                    "value": "value-0",
                },
                {
                    "text": {"type": "plain_text", "text": "*this is plain_text text*"},
                    "value": "value-1",
                },
                {
                    "text": {"type": "plain_text", "text": "*this is plain_text text*"},
                    "value": "value-2",
                },
                {
                    "text": {"type": "plain_text", "text": "*this is plain_text text*"},
                    "value": "value-3",
                },
                {
                    "text": {"type": "plain_text", "text": "*this is plain_text text*"},
                    # https://docs.slack.dev/reference/block-kit/composition-objects/option-object
                    "url": "https://www.example.com",
                },
            ],
            "action_id": "overflow",
        }
        self.assertDictEqual(input, OverflowMenuElement(**input).to_dict())


# -------------------------------------------------
# Input
# -------------------------------------------------


class PlainTextInputElementTests(unittest.TestCase):
    def test_document_1(self):
        input = {
            "type": "plain_text_input",
            "action_id": "plain_input",
            "placeholder": {"type": "plain_text", "text": "Enter some plain text"},
        }
        self.assertDictEqual(input, PlainTextInputElement(**input).to_dict())

    def test_document_2(self):
        input = {
            "type": "plain_text_input",
            "action_id": "plain_input",
            "placeholder": {"type": "plain_text", "text": "Enter some plain text"},
            "initial_value": "TODO",
            "multiline": True,
            "min_length": 1,
            "max_length": 10,
        }
        self.assertDictEqual(input, PlainTextInputElement(**input).to_dict())

    def test_document_3(self):
        input = {
            "type": "plain_text_input",
            "multiline": True,
            "dispatch_action_config": {"trigger_actions_on": ["on_character_entered"]},
        }
        self.assertDictEqual(input, PlainTextInputElement(**input).to_dict())


# -------------------------------------------------
# Radio Buttons
# -------------------------------------------------


class RadioButtonsElementTest(unittest.TestCase):
    def test_document(self):
        input = {
            "type": "radio_buttons",
            "action_id": "this_is_an_action_id",
            "initial_option": {
                "value": "A1",
                "text": {"type": "plain_text", "text": "Radio 1"},
            },
            "options": [
                {"value": "A1", "text": {"type": "plain_text", "text": "Radio 1"}},
                {"value": "A2", "text": {"type": "plain_text", "text": "Radio 2"}},
            ],
            "initial_option": {
                "value": "A2",
                "text": {"type": "plain_text", "text": "Radio 2"},
            },
        }
        self.assertDictEqual(input, RadioButtonsElement(**input).to_dict())
