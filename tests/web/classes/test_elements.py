import unittest

from slack.errors import SlackObjectFormationError
from slack.web.classes.elements import (
    ButtonElement,
    ChannelSelectElement,
    ConversationSelectElement,
    ExternalDataSelectElement,
    ImageElement,
    LinkButtonElement,
    SelectElement,
    UserSelectElement,
)
from slack.web.classes.objects import ConfirmObject, OptionObject
from . import STRING_3001_CHARS, STRING_301_CHARS


class InteractiveElementTests(unittest.TestCase):
    def test_action_id(self):
        with self.assertRaises(SlackObjectFormationError):
            ButtonElement(
                text="click me!", action_id=STRING_301_CHARS, value="clickable button"
            ).get_json()


class ButtonElementTests(unittest.TestCase):
    def test_json(self):
        self.assertDictEqual(
            ButtonElement(
                text="button text", action_id="some_button", value="button_123"
            ).get_json(),
            {
                "text": {"emoji": True, "text": "button text", "type": "plain_text"},
                "action_id": "some_button",
                "value": "button_123",
                "type": "button",
            },
        )
        confirm = ConfirmObject(title="really?", text="are you sure?")

        self.assertDictEqual(
            ButtonElement(
                text="button text",
                action_id="some_button",
                value="button_123",
                style="primary",
                confirm=confirm,
            ).get_json(),
            {
                "text": {"emoji": True, "text": "button text", "type": "plain_text"},
                "action_id": "some_button",
                "value": "button_123",
                "type": "button",
                "style": "primary",
                "confirm": confirm.get_json(),
            },
        )

    def test_text_length(self):
        with self.assertRaises(SlackObjectFormationError):
            ButtonElement(
                text=STRING_301_CHARS, action_id="button", value="click_me"
            ).get_json()

    def test_value_length(self):
        with self.assertRaises(SlackObjectFormationError):
            ButtonElement(
                text="Button", action_id="button", value=STRING_301_CHARS
            ).get_json()

    def test_invalid_style(self):
        with self.assertRaises(SlackObjectFormationError):
            ButtonElement(
                text="Button", action_id="button", value="button", style="invalid"
            ).get_json()


class LinkButtonElementTests(unittest.TestCase):
    def test_json(self):
        button = LinkButtonElement(text="button text", url="http://google.com")
        self.assertDictEqual(
            button.get_json(),
            {
                "text": {"emoji": True, "text": "button text", "type": "plain_text"},
                "url": "http://google.com",
                "type": "button",
                "value": "",
                "action_id": button.action_id,
            },
        )

    def test_url_length(self):
        with self.assertRaises(SlackObjectFormationError):
            LinkButtonElement(text="Button", url=STRING_3001_CHARS).get_json()


class ImageElementTests(unittest.TestCase):
    def test_json(self):
        self.assertDictEqual(
            ImageElement(
                image_url="http://google.com", alt_text="not really an image"
            ).get_json(),
            {
                "image_url": "http://google.com",
                "alt_text": "not really an image",
                "type": "image",
            },
        )

    def test_image_url_length(self):
        with self.assertRaises(SlackObjectFormationError):
            ImageElement(image_url=STRING_3001_CHARS, alt_text="text").get_json()

    def test_alt_text_length(self):
        with self.assertRaises(SlackObjectFormationError):
            ImageElement(
                image_url="http://google.com", alt_text=STRING_3001_CHARS
            ).get_json()


class SelectElementTests(unittest.TestCase):
    option_one = OptionObject.from_single_value("one")
    option_two = OptionObject.from_single_value("two")
    options = [option_one, option_two, OptionObject.from_single_value("three")]

    def test_json(self):
        self.maxDiff = None
        self.assertDictEqual(
            SelectElement(
                placeholder="selectedValue",
                action_id="dropdown",
                options=self.options,
                initial_option=self.option_two,
            ).get_json(),
            {
                "placeholder": {
                    "emoji": True,
                    "text": "selectedValue",
                    "type": "plain_text",
                },
                "action_id": "dropdown",
                "options": [o.get_json("block") for o in self.options],
                "initial_option": self.option_two.get_json(),
                "type": "static_select",
            },
        )

        self.assertDictEqual(
            SelectElement(
                placeholder="selectedValue",
                action_id="dropdown",
                options=self.options,
                confirm=ConfirmObject(title="title", text="text"),
            ).get_json(),
            {
                "placeholder": {
                    "emoji": True,
                    "text": "selectedValue",
                    "type": "plain_text",
                },
                "action_id": "dropdown",
                "options": [o.get_json("block") for o in self.options],
                "confirm": ConfirmObject(title="title", text="text").get_json("block"),
                "type": "static_select",
            },
        )

    def test_options_length(self):
        with self.assertRaises(SlackObjectFormationError):
            SelectElement(
                placeholder="select",
                action_id="selector",
                options=[self.option_one] * 101,
            ).get_json()


class ExternalDropdownElementTests(unittest.TestCase):
    def test_json(self):
        self.assertDictEqual(
            ExternalDataSelectElement(
                placeholder="selectedValue", action_id="dropdown", min_query_length=5
            ).get_json(),
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
        )

        self.assertDictEqual(
            ExternalDataSelectElement(
                placeholder="selectedValue",
                action_id="dropdown",
                confirm=ConfirmObject(title="title", text="text"),
            ).get_json(),
            {
                "placeholder": {
                    "emoji": True,
                    "text": "selectedValue",
                    "type": "plain_text",
                },
                "action_id": "dropdown",
                "confirm": ConfirmObject(title="title", text="text").get_json("block"),
                "type": "external_select",
            },
        )


class DynamicDropdownTests(unittest.TestCase):
    dynamic_types = {UserSelectElement, ConversationSelectElement, ChannelSelectElement}

    def test_json(self):
        for dropdown_type in self.dynamic_types:
            with self.subTest(dropdown_type=dropdown_type):
                self.assertDictEqual(
                    dropdown_type(
                        placeholder="abc", action_id="dropdown", initial_value="def"
                    ).get_json(),
                    {
                        "placeholder": {
                            "emoji": True,
                            "text": "abc",
                            "type": "plain_text",
                        },
                        "action_id": "dropdown",
                        f"initial_{dropdown_type.initial_object_type}": "def",
                        "type": f"{dropdown_type.initial_object_type}s_select",
                    },
                )
