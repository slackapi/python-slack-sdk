import unittest

from slack.errors import SlackObjectFormationError
from slack.web.classes.elements import (
    ButtonElement, ChannelDropdownElement, ConversationDropdownElement, DropdownElement,
    ExternalDropdownElement, ImageElement, LinkButtonElement, UserDropdownElement)
from slack.web.classes.objects import ConfirmObject, SimpleOption
from tests.web.classes import compare_json_structure
from . import STRING_3001_CHARS, STRING_301_CHARS


class InteractiveElementTests(unittest.TestCase):
    def test_action_id(self):
        with self.assertRaises(SlackObjectFormationError):
            ButtonElement(
                text="click me!", action_id=STRING_301_CHARS, value="clickable button"
            ).get_json()


class ButtonElementTests(unittest.TestCase):
    def test_json(self):
        self.assertTrue(
            compare_json_structure(
                clazz=ButtonElement,
                kwargs={
                    "text": "button text",
                    "action_id": "some_button",
                    "value": "button_123",
                    "style": None,
                    "confirm": None,
                },
                attributes={"type": "button"},
            )
        )
        self.assertTrue(
            compare_json_structure(
                clazz=ButtonElement,
                kwargs={
                    "text": "button text",
                    "action_id": "some_button",
                    "value": "button_123",
                    "style": "primary",
                    "confirm": ConfirmObject(
                        title="confirm_title", text="confirm_text"
                    ),
                },
                attributes={"type": "button"},
            )
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
        self.assertTrue(
            compare_json_structure(
                clazz=LinkButtonElement,
                kwargs={"text": "button text", "url": "http://google.com"},
                attributes={"type": "button"},
            )
        )

    def test_url_length(self):
        with self.assertRaises(SlackObjectFormationError):
            LinkButtonElement(text="Button", url=STRING_3001_CHARS).get_json()


class ImageElementTests(unittest.TestCase):
    def test_json(self):
        self.assertTrue(
            compare_json_structure(
                clazz=ImageElement,
                kwargs={
                    "image_url": "http://google.com",
                    "alt_text": "not really an image",
                },
                attributes={"type": "image"},
            )
        )

    def test_image_url_length(self):
        with self.assertRaises(SlackObjectFormationError):
            ImageElement(image_url=STRING_3001_CHARS, alt_text="text").get_json()

    def test_alt_text_length(self):
        with self.assertRaises(SlackObjectFormationError):
            ImageElement(
                image_url="http://google.com", alt_text=STRING_3001_CHARS
            ).get_json()


class DropdownElementTests(unittest.TestCase):
    option_one = SimpleOption(label="one")
    option_two = SimpleOption(label="two")
    options = [option_one, option_two, SimpleOption(label="three")]

    def test_json(self):
        self.assertTrue(
            compare_json_structure(
                clazz=DropdownElement,
                kwargs={
                    "placeholder": "selectedValue",
                    "action_id": "dropdown",
                    "options": self.options,
                    "initial_option": self.option_two,
                },
                attributes={"type": "static_select"},
            )
        )

        self.assertTrue(
            compare_json_structure(
                clazz=DropdownElement,
                kwargs={
                    "placeholder": "selectedValue",
                    "action_id": "dropdown",
                    "options": self.options,
                    "confirm": ConfirmObject(title="title", text="text"),
                },
                attributes={"type": "static_select"},
            )
        )

    def test_options_length(self):
        with self.assertRaises(SlackObjectFormationError):
            DropdownElement(
                placeholder="select",
                action_id="selector",
                options=[self.option_one] * 101,
            ).get_json()


class ExternalDropdownElementTests(unittest.TestCase):
    def test_json(self):
        self.assertTrue(
            compare_json_structure(
                clazz=ExternalDropdownElement,
                kwargs={
                    "placeholder": "selectedValue",
                    "action_id": "dropdown",
                    "min_query_length": 5,
                },
                attributes={"type": "external_select"},
            )
        )

        self.assertTrue(
            compare_json_structure(
                clazz=ExternalDropdownElement,
                kwargs={
                    "placeholder": "selectedValue",
                    "action_id": "dropdown",
                    "confirm": ConfirmObject(title="title", text="text"),
                },
                attributes={"type": "external_select"},
            )
        )


class DynamicDropdownTests(unittest.TestCase):
    dynamic_types = {
        UserDropdownElement,
        ConversationDropdownElement,
        ChannelDropdownElement,
    }

    def test_json(self):
        for dropdown_type in self.dynamic_types:
            with self.subTest(dropdown_type=dropdown_type):
                self.assertTrue(
                    compare_json_structure(
                        clazz=dropdown_type,
                        kwargs={
                            "placeholder": "abc",
                            "action_id": "dropdown",
                            "initial_value": "def",
                        },
                        attributes={
                            "type": f"{dropdown_type.initial_object_type}s_select"
                        },
                    )
                )
