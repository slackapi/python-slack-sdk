import unittest

from slack_sdk.errors import SlackObjectFormationError
from slack_sdk.models.blocks import (
    BlockElement,
    ButtonElement,
    ChannelMultiSelectElement,
    ChannelSelectElement,
    CheckboxesElement,
    ConfirmObject,
    ConversationMultiSelectElement,
    ConversationSelectElement,
    DatePickerElement,
    ExternalDataMultiSelectElement,
    ExternalDataSelectElement,
    FeedbackButtonsElement,
    IconButtonElement,
    ImageElement,
    InputInteractiveElement,
    InteractiveElement,
    LinkButtonElement,
    Option,
    OverflowMenuElement,
    PlainTextInputElement,
    PlainTextObject,
    RadioButtonsElement,
    RichTextBlock,
    StaticMultiSelectElement,
    StaticSelectElement,
    TimePickerElement,
    UserMultiSelectElement,
    UserSelectElement,
)
from slack_sdk.models.blocks.basic_components import SlackFile
from slack_sdk.models.blocks.block_elements import (
    DateTimePickerElement,
    EmailInputElement,
    FileInputElement,
    NumberInputElement,
    RichTextElementParts,
    RichTextInputElement,
    RichTextSectionElement,
    UrlInputElement,
    WorkflowButtonElement,
)

from . import STRING_301_CHARS, STRING_3001_CHARS


class BlockElementTests(unittest.TestCase):
    def test_eq(self):
        self.assertEqual(BlockElement(), BlockElement())
        self.assertEqual(BlockElement(type="test"), BlockElement(type="test"))
        self.assertNotEqual(BlockElement(type="test"), BlockElement(type="another test"))

    def test_parse_timepicker(self):
        timepicker = BlockElement.parse(
            {
                "type": "timepicker",
                "action_id": "timepicker123",
                "initial_time": "11:40",
                "placeholder": {
                    "type": "plain_text",
                    "text": "Select a time",
                },
            }
        )
        self.assertIsNotNone(timepicker)
        self.assertEqual(timepicker.type, TimePickerElement.type)


# -------------------------------------------------
# Interactive Elements
# -------------------------------------------------


class InteractiveElementTests(unittest.TestCase):
    def test_with_interactive_element(self):
        input = {"type": "plain_text_input", "action_id": "plain_input"}
        # Any properties should not be lost
        self.assertDictEqual(input, InteractiveElement(**input).to_dict())

    def test_with_input_interactive_element(self):
        input = {
            "type": "plain_text_input",
            "action_id": "plain_input",
            "placeholder": {"type": "plain_text", "text": "Enter some plain text"},
            "focus_on_load": True,
        }
        # Any properties should not be lost
        self.assertDictEqual(input, InputInteractiveElement(**input).to_dict())


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

    def test_document_4(self):
        input = {
            "type": "button",
            "text": {"type": "plain_text", "text": "Save"},
            "style": "primary",
            "value": "click_me_123",
            "action_id": "button",
            "accessibility_label": "This label will be read out by screen readers",
        }
        self.assertDictEqual(input, ButtonElement(**input).to_dict())

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

    def test_action_id_length(self):
        with self.assertRaises(SlackObjectFormationError):
            ButtonElement(text="test", action_id="1234567890" * 26, value="click_me").to_dict()

    def test_value_length(self):
        with self.assertRaises(SlackObjectFormationError):
            ButtonElement(text="Button", action_id="button", value=STRING_3001_CHARS).to_dict()

    def test_invalid_style(self):
        with self.assertRaises(SlackObjectFormationError):
            ButtonElement(text="Button", action_id="button", value="button", style="invalid").to_dict()

    def test_accessibility_label_length(self):
        with self.assertRaises(SlackObjectFormationError):
            ButtonElement(
                text="Hi there!",
                action_id="button",
                value="click_me",
                accessibility_label=("1234567890" * 8),
            ).to_dict()

    def test_action_id(self):
        with self.assertRaises(SlackObjectFormationError):
            ButtonElement(text="click me!", action_id=STRING_301_CHARS, value="clickable button").to_dict()


class LinkButtonElementTests(unittest.TestCase):
    def test_json(self):
        button = LinkButtonElement(action_id="test", text="button text", url="https://example.com")
        self.assertDictEqual(
            {
                "text": {"emoji": True, "text": "button text", "type": "plain_text"},
                "url": "https://example.com",
                "type": "button",
                "action_id": button.action_id,
            },
            button.to_dict(),
        )

    # https://github.com/slackapi/python-slack-sdk/issues/1178
    def test_text_patterns_issue_1178(self):
        button = LinkButtonElement(
            action_id="test",
            text=PlainTextObject(text="button text"),
            url="http://slack.com",
        )
        self.assertDictEqual(
            {
                "text": {"text": "button text", "type": "plain_text"},
                "url": "http://slack.com",
                "type": "button",
                "action_id": button.action_id,
            },
            button.to_dict(),
        )

    def test_url_length(self):
        with self.assertRaises(SlackObjectFormationError):
            LinkButtonElement(text="Button", url=STRING_3001_CHARS).to_dict()

    def test_action_id_length(self):
        with self.assertRaises(SlackObjectFormationError):
            LinkButtonElement(
                text="test",
                action_id="1234567890" * 26,
                value="click_me",
                url="https://slack.com/",
            ).to_dict()


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

    def test_focus_on_load(self):
        input = {
            "type": "checkboxes",
            "action_id": "this_is_an_action_id",
            "initial_options": [{"value": "A1", "text": {"type": "plain_text", "text": "Checkbox 1"}}],
            "options": [
                {"value": "A1", "text": {"type": "plain_text", "text": "Checkbox 1"}},
            ],
            "focus_on_load": True,
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

    def test_focus_on_load(self):
        input = {
            "type": "datepicker",
            "action_id": "datepicker123",
            "initial_date": "1990-04-28",
            "placeholder": {"type": "plain_text", "text": "Select a date"},
            "focus_on_load": True,
        }
        self.assertDictEqual(input, DatePickerElement(**input).to_dict())


# -------------------------------------------------
# TimePicker
# -------------------------------------------------


class TimePickerElementTests(unittest.TestCase):
    def test_document(self):
        input = {
            "type": "timepicker",
            "action_id": "timepicker123",
            "initial_time": "11:40",
            "placeholder": {
                "type": "plain_text",
                "text": "Select a time",
            },
        }
        self.assertDictEqual(input, TimePickerElement(**input).to_dict())

    def test_json(self):
        for hour in range(0, 23):
            for minute in range(0, 59):
                time = f"{hour:02}:{minute:02}"
                self.assertDictEqual(
                    {
                        "action_id": "timepicker123",
                        "initial_time": time,
                        "placeholder": {
                            "emoji": True,
                            "type": "plain_text",
                            "text": "Select a time",
                        },
                        "type": "timepicker",
                    },
                    TimePickerElement(
                        action_id="timepicker123",
                        placeholder="Select a time",
                        initial_time=time,
                    ).to_dict(),
                )

        with self.assertRaises(SlackObjectFormationError):
            TimePickerElement(
                action_id="timepicker123",
                placeholder="Select a time",
                initial_time="25:00",
            ).to_dict()

    def test_focus_on_load(self):
        input = {
            "type": "timepicker",
            "action_id": "timepicker123",
            "initial_time": "11:40",
            "placeholder": {
                "type": "plain_text",
                "text": "Select a time",
            },
            "focus_on_load": True,
        }
        self.assertDictEqual(input, TimePickerElement(**input).to_dict())

    def test_timezone(self):
        input = {
            "type": "timepicker",
            "action_id": "timepicker123",
            "initial_time": "11:40",
            "placeholder": {
                "type": "plain_text",
                "text": "Select a time",
            },
            "timezone": "America/Los_Angeles",
        }
        self.assertDictEqual(input, TimePickerElement(**input).to_dict())


# -------------------------------------------------
# DateTimePicker
# -------------------------------------------------


class DateTimePickerElementTests(unittest.TestCase):
    def test_document(self):
        input = {"type": "datetimepicker", "action_id": "datetimepicker123", "initial_date_time": 1628633820}
        self.assertDictEqual(input, DateTimePickerElement(**input).to_dict())

    def test_json(self):
        for initial_date_time in [0, 9999999999]:
            self.assertDictEqual(
                {
                    "action_id": "datetimepicker123",
                    "initial_date_time": initial_date_time,
                    "type": "datetimepicker",
                },
                DateTimePickerElement(
                    action_id="datetimepicker123",
                    initial_date_time=initial_date_time,
                ).to_dict(),
            )

        with self.assertRaises(SlackObjectFormationError):
            DateTimePickerElement(
                action_id="datetimepicker123",
                initial_date_time=10000000000,
            ).to_dict()

    def test_focus_on_load(self):
        input = {
            "type": "datetimepicker",
            "action_id": "datetimepicker123",
            "initial_date_time": 1628633820,
            "focus_on_load": True,
        }
        self.assertDictEqual(input, DateTimePickerElement(**input).to_dict())


# ----------------------------------------------
# FeedbackButtons
# ----------------------------------------------


class FeedbackButtonsTests(unittest.TestCase):
    def test_document(self):
        input = {
            "type": "feedback_buttons",
            "action_id": "feedback-123",
            "positive_button": {
                "text": {"type": "plain_text", "text": "+1"},
                "accessibility_label": "Positive feedback",
                "value": "positive",
            },
            "negative_button": {
                "text": {"type": "plain_text", "text": "-1"},
                "accessibility_label": "Negative feedback",
                "value": "negative",
            },
        }
        self.assertDictEqual(input, FeedbackButtonsElement(**input).to_dict())


# ----------------------------------------------
# IconButton
# ----------------------------------------------


class IconButtonTests(unittest.TestCase):
    def test_document(self):
        input = {
            "type": "icon_button",
            "action_id": "icon-123",
            "icon": "trash",
            "text": {"type": "plain_text", "text": "Delete"},
            "accessibility_label": "Delete item",
            "value": "delete_item",
            "visible_to_user_ids": ["U123456", "U789012"],
        }
        self.assertDictEqual(input, IconButtonElement(**input).to_dict())

    def test_with_confirm(self):
        input = {
            "type": "icon_button",
            "action_id": "icon-456",
            "icon": "trash",
            "text": {"type": "plain_text", "text": "Delete"},
            "value": "trash",
            "confirm": {
                "title": {"type": "plain_text", "text": "Are you sure?"},
                "text": {"type": "plain_text", "text": "This will send a warning."},
                "confirm": {"type": "plain_text", "text": "Yes"},
                "deny": {"type": "plain_text", "text": "No"},
            },
        }
        icon_button = IconButtonElement(**input)
        self.assertIsNotNone(icon_button.confirm)
        self.assertDictEqual(input, icon_button.to_dict())


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
                "image_url": "https://example.com",
                "alt_text": "not really an image",
                "type": "image",
            },
            ImageElement(image_url="https://example.com", alt_text="not really an image").to_dict(),
        )

    def test_image_url_length(self):
        with self.assertRaises(SlackObjectFormationError):
            ImageElement(image_url=STRING_3001_CHARS, alt_text="text").to_dict()

    def test_alt_text_length(self):
        with self.assertRaises(SlackObjectFormationError):
            ImageElement(image_url="https://example.com", alt_text=STRING_3001_CHARS).to_dict()

    def test_slack_file(self):
        self.assertDictEqual(
            {
                "slack_file": {"id": "F11111"},
                "alt_text": "not really an image",
                "type": "image",
            },
            ImageElement(slack_file=SlackFile(id="F11111"), alt_text="not really an image").to_dict(),
        )
        self.assertDictEqual(
            {
                "slack_file": {"url": "https://example.com"},
                "alt_text": "not really an image",
                "type": "image",
            },
            ImageElement(slack_file=SlackFile(url="https://example.com"), alt_text="not really an image").to_dict(),
        )
        self.assertDictEqual(
            {
                "slack_file": {"id": "F11111"},
                "alt_text": "not really an image",
                "type": "image",
            },
            ImageElement(slack_file={"id": "F11111"}, alt_text="not really an image").to_dict(),
        )
        self.assertDictEqual(
            {
                "slack_file": {"url": "https://example.com"},
                "alt_text": "not really an image",
                "type": "image",
            },
            ImageElement(slack_file={"url": "https://example.com"}, alt_text="not really an image").to_dict(),
        )


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

    def test_focus_on_load(self):
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
            "focus_on_load": True,
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

    def test_focus_on_load(self):
        input = {
            "action_id": "text1234",
            "type": "static_select",
            "placeholder": {"type": "plain_text", "text": "Select an item"},
            "options": [
                {
                    "text": {"type": "plain_text", "text": "*this is plain_text text*"},
                    "value": "value-0",
                },
            ],
            "focus_on_load": True,
        }
        self.assertDictEqual(input, StaticSelectElement(**input).to_dict())

    def test_lists_and_tuples_serialize_to_dict_equally(self):
        expected = {
            "options": [
                {
                    "text": {"emoji": True, "text": "X", "type": "plain_text"},
                    "value": "x",
                }
            ],
            "type": "static_select",
        }
        option = Option(value="x", text="X")
        # List
        self.assertDictEqual(
            expected,
            StaticSelectElement(options=[option]).to_dict(),
        )
        # Tuple (this pattern used to be failing)
        self.assertDictEqual(
            expected,
            StaticSelectElement(options=(option,)).to_dict(),
        )


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

    def test_focus_on_load(self):
        input = {
            "action_id": "text1234",
            "type": "multi_external_select",
            "placeholder": {"type": "plain_text", "text": "Select items"},
            "focus_on_load": True,
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

    def test_focus_on_load(self):
        input = {
            "action_id": "text1234",
            "type": "external_select",
            "placeholder": {"type": "plain_text", "text": "Select an item"},
            "focus_on_load": True,
        }
        self.assertDictEqual(input, ExternalDataSelectElement(**input).to_dict())


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

    def test_focus_on_load(self):
        input = {
            "action_id": "text1234",
            "type": "users_select",
            "placeholder": {"type": "plain_text", "text": "Select an item"},
            "initial_user": "U123",
            "focus_on_load": True,
        }
        self.assertDictEqual(input, UserSelectElement(**input).to_dict())


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

    def test_focus_on_load(self):
        input = {
            "action_id": "text1234",
            "type": "multi_conversations_select",
            "placeholder": {"type": "plain_text", "text": "Select conversations"},
            "initial_conversations": ["C123", "C234"],
            "focus_on_load": True,
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

    def test_focus_on_load(self):
        input = {
            "action_id": "text1234",
            "type": "conversations_select",
            "placeholder": {"type": "plain_text", "text": "Select an item"},
            "initial_conversation": "C123",
            "focus_on_load": True,
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

    def test_focus_on_load(self):
        input = {
            "action_id": "text1234",
            "type": "multi_channels_select",
            "placeholder": {"type": "plain_text", "text": "Select channels"},
            "initial_channels": ["C123", "C234"],
            "focus_on_load": True,
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

    def test_focus_on_load(self):
        input = {
            "action_id": "text1234",
            "type": "channels_select",
            "placeholder": {"type": "plain_text", "text": "Select an item"},
            "focus_on_load": True,
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


class RichTextInputElementTests(unittest.TestCase):
    def test_simple(self):
        input = {
            "type": "rich_text_input",
            "action_id": "rich_input",
            "placeholder": {"type": "plain_text", "text": "Enter some plain text"},
        }
        self.assertDictEqual(input, RichTextInputElement(**input).to_dict())

    def test_document(self):
        input = {
            "type": "rich_text_input",
            "action_id": "rich_text_input-action",
            "dispatch_action_config": {"trigger_actions_on": ["on_character_entered"]},
            "focus_on_load": True,
            "placeholder": {"type": "plain_text", "text": "Enter text"},
        }
        self.assertDictEqual(input, RichTextInputElement(**input).to_dict())

    def test_issue_1571(self):
        self.assertDictEqual(
            RichTextInputElement(
                action_id="contents",
                initial_value=RichTextBlock(
                    elements=[
                        RichTextSectionElement(
                            elements=[
                                RichTextElementParts.Text(text="Hey, "),
                                RichTextElementParts.Text(text="this", style={"italic": True}),
                                RichTextElementParts.Text(text="is what you should be looking at. "),
                                RichTextElementParts.Text(text="Please", style={"bold": True}),
                            ]
                        )
                    ],
                ),
            ).to_dict(),
            {
                "action_id": "contents",
                "initial_value": {
                    "elements": [
                        {
                            "elements": [
                                {"text": "Hey, ", "type": "text"},
                                {"style": {"italic": True}, "text": "this", "type": "text"},
                                {"text": "is what you should be looking at. ", "type": "text"},
                                {"style": {"bold": True}, "text": "Please", "type": "text"},
                            ],
                            "type": "rich_text_section",
                        }
                    ],
                    "type": "rich_text",
                },
                "type": "rich_text_input",
            },
        )


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

    def test_focus_on_load(self):
        input = {
            "type": "plain_text_input",
            "action_id": "plain_input",
            "placeholder": {"type": "plain_text", "text": "Enter some plain text"},
            "focus_on_load": True,
        }
        self.assertDictEqual(input, PlainTextInputElement(**input).to_dict())


# -------------------------------------------------
# Email Input Element
# -------------------------------------------------


class EmailInputElementTests(unittest.TestCase):
    def test_element(self):
        input = {
            "type": "email_text_input",
            "action_id": "email_text_input-action",
            "placeholder": {"type": "plain_text", "text": "Enter some email"},
        }
        self.assertDictEqual(input, EmailInputElement(**input).to_dict())

    def test_initial_value(self):
        input = {
            "type": "email_text_input",
            "action_id": "email_text_input-action",
            "initial_value": "bill@slack.com",
            "placeholder": {"type": "plain_text", "text": "Enter some email"},
        }
        self.assertDictEqual(input, EmailInputElement(**input).to_dict())

    def test_no_action_id(self):
        input = {
            "type": "email_text_input",
            "dispatch_action_config": {"trigger_actions_on": ["on_character_entered"]},
        }
        self.assertDictEqual(input, EmailInputElement(**input).to_dict())

    def test_focus_on_load(self):
        input = {
            "type": "email_text_input",
            "action_id": "email_text_input-action",
            "placeholder": {"type": "plain_text", "text": "Enter some email"},
            "focus_on_load": True,
        }
        self.assertDictEqual(input, EmailInputElement(**input).to_dict())


# -------------------------------------------------
# Url Input Element
# -------------------------------------------------


class UrlInputElementTests(unittest.TestCase):
    def test_element(self):
        input = {
            "type": "url_text_input",
            "action_id": "url_text_input-action",
            "placeholder": {"type": "plain_text", "text": "Enter some url"},
        }
        self.assertDictEqual(input, UrlInputElement(**input).to_dict())

    def test_initial_value(self):
        input = {
            "type": "url_text_input",
            "action_id": "url_text_input-action",
            "initial_value": "https://bill.test.com",
            "placeholder": {"type": "plain_text", "text": "Enter some url"},
        }
        self.assertDictEqual(input, UrlInputElement(**input).to_dict())

    def test_no_action_id(self):
        input = {
            "type": "url_text_input",
            "dispatch_action_config": {"trigger_actions_on": ["on_character_entered"]},
        }
        self.assertDictEqual(input, UrlInputElement(**input).to_dict())

    def test_focus_on_load(self):
        input = {
            "type": "url_text_input",
            "action_id": "url_text_input-action",
            "placeholder": {"type": "plain_text", "text": "Enter some url"},
            "focus_on_load": True,
        }
        self.assertDictEqual(input, UrlInputElement(**input).to_dict())


# -------------------------------------------------
# Number Input Element
# -------------------------------------------------


class NumberInputElementTests(unittest.TestCase):
    def test_element(self):
        input = {
            "type": "number_input",
            "action_id": "number_input-action",
            "is_decimal_allowed": False,
            "placeholder": {"type": "plain_text", "text": "Enter some plain text"},
        }
        self.assertDictEqual(input, NumberInputElement(**input).to_dict())

    def test_element_full(self):
        input = {
            "type": "number_input",
            "action_id": "number_input-action",
            "is_decimal_allowed": False,
            "placeholder": {"type": "plain_text", "text": "Enter some plain text"},
            "initial_value": "7",
            "min_value": "1",
            "max_value": "10",
        }
        self.assertDictEqual(input, NumberInputElement(**input).to_dict())

    def test_dispatch_action_config(self):
        input = {
            "type": "number_input",
            "is_decimal_allowed": True,
            "dispatch_action_config": {"trigger_actions_on": ["on_character_entered"]},
        }
        self.assertDictEqual(input, NumberInputElement(**input).to_dict())

    def test_focus_on_load(self):
        input = {
            "type": "number_input",
            "action_id": "number_input-action",
            "is_decimal_allowed": False,
            "placeholder": {"type": "plain_text", "text": "Enter some plain text"},
            "focus_on_load": True,
        }
        self.assertDictEqual(input, NumberInputElement(**input).to_dict())


# -------------------------------------------------
# File Input Element
# -------------------------------------------------


class FileInputElementTests(unittest.TestCase):
    def test_element(self):
        input = {
            "type": "file_input",
            "action_id": "file_input-action",
            "filetypes": ["pdf", "txt"],
            "max_files": 3,
        }
        self.assertDictEqual(input, FileInputElement(**input).to_dict())


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
        }
        self.assertDictEqual(input, RadioButtonsElement(**input).to_dict())

    def test_focus_on_load(self):
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
            "focus_on_load": True,
        }
        self.assertDictEqual(input, RadioButtonsElement(**input).to_dict())


# -------------------------------------------------
# Workflow Button
# -------------------------------------------------


class WorkflowButtonElementTests(unittest.TestCase):
    def test_load(self):
        input = {
            "type": "workflow_button",
            "text": {"type": "plain_text", "text": "Run Workflow"},
            "workflow": {
                "trigger": {
                    "url": "https://slack.com/shortcuts/Ft0123ABC456/xyz...zyx",
                    "customizable_input_parameters": [
                        {"name": "input_parameter_a", "value": "Value for input param A"},
                        {"name": "input_parameter_b", "value": "Value for input param B"},
                    ],
                }
            },
        }
        self.assertDictEqual(input, WorkflowButtonElement(**input).to_dict())
