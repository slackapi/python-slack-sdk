import unittest

from slack.errors import SlackObjectFormationError
from slack.web.classes.actions import (
    ActionButton,
    ActionChannelSelector,
    ActionConversationSelector,
    ActionExternalSelector,
    ActionLinkButton,
    ActionStaticSelector,
    ActionUserSelector,
)
from slack.web.classes.objects import ConfirmObject, Option, OptionGroup
from tests.web.classes import STRING_3001_CHARS


class ButtonTests(unittest.TestCase):
    def test_json(self):
        self.assertDictEqual(
            ActionButton(name="button_1", text="Click me!", value="btn_1").get_json(),
            {
                "name": "button_1",
                "text": "Click me!",
                "value": "btn_1",
                "type": "button",
            },
        )

        confirm = ConfirmObject(title="confirm_title", text="confirm_text")
        self.assertDictEqual(
            ActionButton(
                name="button_1",
                text="Click me!",
                value="btn_1",
                confirm=confirm,
                style="danger",
            ).get_json(),
            {
                "name": "button_1",
                "text": "Click me!",
                "value": "btn_1",
                "type": "button",
                "confirm": confirm.get_json("action"),
                "style": "danger",
            },
        )

    def test_value_length(self):
        with self.assertRaises(SlackObjectFormationError):
            ActionButton(
                name="button_1", text="Click me!", value=STRING_3001_CHARS
            ).get_json()

    def test_style_validator(self):
        b = ActionButton(name="button_1", text="Click me!", value="btn_1")
        with self.assertRaises(SlackObjectFormationError):
            b.style = "abcdefg"
            b.get_json()

        b.style = "primary"
        b.get_json()


class LinkButtonTests(unittest.TestCase):
    def test_json(self):
        self.assertDictEqual(
            ActionLinkButton(text="Click me!", url="http://google.com").get_json(),
            {"url": "http://google.com", "text": "Click me!", "type": "button"},
        )


class StaticActionSelectorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.options = [
            Option.from_single_value("one"),
            Option.from_single_value("two"),
            Option.from_single_value("three"),
        ]

        self.option_group = [OptionGroup(label="group_1", options=self.options)]

    def test_json(self):
        self.assertDictEqual(
            ActionStaticSelector(
                name="select_1", text="selector_1", options=self.options
            ).get_json(),
            {
                "name": "select_1",
                "text": "selector_1",
                "options": [o.get_json("action") for o in self.options],
                "type": "select",
                "data_source": "static",
            },
        )

        self.assertDictEqual(
            ActionStaticSelector(
                name="select_1", text="selector_1", options=self.option_group
            ).get_json(),
            {
                "name": "select_1",
                "text": "selector_1",
                "option_groups": [o.get_json("action") for o in self.option_group],
                "type": "select",
                "data_source": "static",
            },
        )

    def test_options_length(self):
        with self.assertRaises(SlackObjectFormationError):
            ActionStaticSelector(
                name="select_1", text="selector_1", options=self.options * 34
            ).get_json()


class DynamicActionSelectorTests(unittest.TestCase):
    selectors = {ActionUserSelector, ActionChannelSelector, ActionConversationSelector}

    def setUp(self) -> None:
        self.selected_opt = Option.from_single_value("U12345")

    def test_json(self):
        for component in self.selectors:
            with self.subTest(msg=f"{component} json formation test"):
                self.assertDictEqual(
                    component(name="select_1", text="selector_1").get_json(),
                    {
                        "name": "select_1",
                        "text": "selector_1",
                        "type": "select",
                        "data_source": component.data_source,
                    },
                )

                self.assertDictEqual(
                    component(
                        name="select_1",
                        text="selector_1",
                        # next line is a little silly, but so is writing the test
                        # three times
                        **{f"selected_{component.data_source[:-1]}": self.selected_opt},
                    ).get_json(),
                    {
                        "name": "select_1",
                        "text": "selector_1",
                        "type": "select",
                        "data_source": component.data_source,
                        "selected_options": [self.selected_opt.get_json("action")],
                    },
                )


class ExternalActionSelectorTests(unittest.TestCase):
    def test_json(self):
        option = Option.from_single_value("one")

        self.assertDictEqual(
            ActionExternalSelector(
                name="select_1", text="selector_1", min_query_length=3
            ).get_json(),
            {
                "name": "select_1",
                "text": "selector_1",
                "min_query_length": 3,
                "type": "select",
                "data_source": "external",
            },
        )

        self.assertDictEqual(
            ActionExternalSelector(
                name="select_1", text="selector_1", selected_option=option
            ).get_json(),
            {
                "name": "select_1",
                "text": "selector_1",
                "selected_options": [option.get_json("action")],
                "type": "select",
                "data_source": "external",
            },
        )
