import unittest
from copy import copy

from slack.errors import SlackObjectFormationError
from slack.web.classes.dialog_elements import (
    DialogChannelSelector,
    DialogConversationSelector,
    DialogExternalSelector,
    DialogStaticSelector,
    DialogTextArea,
    DialogTextField,
    DialogUserSelector,
)
from slack.web.classes.dialogs import DialogBuilder
from slack.web.classes.objects import Option
from . import STRING_3001_CHARS, STRING_301_CHARS, STRING_51_CHARS

TextComponents = {DialogTextField, DialogTextArea}


class CommonTextComponentTests(unittest.TestCase):
    def test_json_validators(self):
        for component in TextComponents:
            with self.subTest(f"Component: {component}"):
                with self.assertRaises(SlackObjectFormationError, msg="name length"):
                    component(name=STRING_301_CHARS, label="label ").to_dict()

                with self.assertRaises(SlackObjectFormationError, msg="label length"):
                    component(name="dialog", label=STRING_51_CHARS).to_dict()

                with self.assertRaises(SlackObjectFormationError, msg="placeholder length"):
                    component(name="dialog", label="Dialog", placeholder=STRING_301_CHARS).to_dict()

                with self.assertRaises(SlackObjectFormationError, msg="hint length"):
                    component(name="dialog", label="Dialog", hint=STRING_301_CHARS).to_dict()

                with self.assertRaises(SlackObjectFormationError, msg="value length"):
                    component(name="dialog", label="Dialog", value=STRING_3001_CHARS).to_dict()

                with self.assertRaises(SlackObjectFormationError, msg="min_length out of bounds"):
                    component(
                        name="dialog",
                        label="Dialog",
                        min_length=component.max_value_length + 1,
                    ).to_dict()

                with self.assertRaises(SlackObjectFormationError, msg="max_length out of bounds"):
                    component(
                        name="dialog",
                        label="Dialog",
                        max_length=component.max_value_length + 1,
                    ).to_dict()

                with self.assertRaises(SlackObjectFormationError, msg="min_length > max length"):
                    component(name="dialog", label="Dialog", min_length=100, max_length=50).to_dict()

                with self.assertRaises(SlackObjectFormationError, msg="subtype invalid"):
                    component(name="dialog", label="Dialog", subtype="abcdefg").to_dict()


class TextFieldComponentTests(unittest.TestCase):
    def test_json(self):
        self.assertDictEqual(
            DialogTextField(name="dialog", label="Dialog").to_dict(),
            {
                "name": "dialog",
                "label": "Dialog",
                "min_length": 0,
                "max_length": 150,
                "optional": False,
                "type": "text",
            },
        )

    def test_basic_json(self):
        self.assertDictEqual(
            DialogTextField(
                name="dialog",
                label="Dialog",
                optional=True,
                hint="Some hint",
                max_length=100,
                min_length=20,
            ).to_dict(),
            {
                "min_length": 20,
                "max_length": 100,
                "name": "dialog",
                "optional": True,
                "label": "Dialog",
                "type": "text",
                "hint": "Some hint",
            },
        )


class TextAreaComponentTests(unittest.TestCase):
    def test_basic_json_formation(self):
        self.assertDictEqual(
            DialogTextArea(name="dialog", label="Dialog").to_dict(),
            {
                "min_length": 0,
                "max_length": 3000,
                "name": "dialog",
                "optional": False,
                "label": "Dialog",
                "type": "textarea",
            },
        )

    def test_complex_json_formation(self):
        self.assertDictEqual(
            DialogTextArea(
                name="dialog",
                label="Dialog",
                optional=True,
                hint="Some hint",
                max_length=500,
                min_length=100,
            ).to_dict(),
            {
                "min_length": 100,
                "max_length": 500,
                "name": "dialog",
                "optional": True,
                "label": "Dialog",
                "type": "textarea",
                "hint": "Some hint",
            },
        )


class StaticDropdownTests(unittest.TestCase):
    def test_basic_json_formation(self):
        options = [
            Option.from_single_value("one"),
            Option.from_single_value("two"),
            Option.from_single_value("three"),
        ]
        self.assertDictEqual(
            DialogStaticSelector(name="dialog", label="Dialog", options=options).to_dict(),
            {
                "optional": False,
                "label": "Dialog",
                "type": "select",
                "name": "dialog",
                "options": [
                    {"label": "one", "value": "one"},
                    {"label": "two", "value": "two"},
                    {"label": "three", "value": "three"},
                ],
                "data_source": "static",
            },
        )


class DynamicSelectorTests(unittest.TestCase):
    selectors = {DialogUserSelector, DialogChannelSelector, DialogConversationSelector}

    def setUp(self) -> None:
        self.selected_opt = Option.from_single_value("U12345")

    def test_json(self):
        self.maxDiff = None
        for component in self.selectors:
            with self.subTest(msg=f"{component} json formation test"):
                self.assertDictEqual(
                    component(name="select_1", label="selector_1").to_dict(),
                    {
                        "name": "select_1",
                        "label": "selector_1",
                        "type": "select",
                        "optional": False,
                        "data_source": component.data_source,
                    },
                )

                passing_obj = component(name="select_1", label="selector_1", value=self.selected_opt).to_dict()

                passing_str = component(name="select_1", label="selector_1", value="U12345").to_dict()

                expected = {
                    "name": "select_1",
                    "label": "selector_1",
                    "type": "select",
                    "optional": False,
                    "data_source": component.data_source,
                    "value": "U12345",
                }
                self.assertDictEqual(passing_obj, expected)
                self.assertDictEqual(passing_str, expected)


class ExternalSelectorTests(unittest.TestCase):
    def test_basic_json_formation(self):
        o = Option.from_single_value("one")
        self.assertDictEqual(
            DialogExternalSelector(
                name="dialog",
                label="Dialog",
                value=o,
                min_query_length=3,
                optional=True,
                placeholder="something",
            ).to_dict(),
            {
                "optional": True,
                "label": "Dialog",
                "type": "select",
                "name": "dialog",
                "min_query_length": 3,
                "placeholder": "something",
                "selected_options": [o.to_dict("dialog")],
                "data_source": "external",
            },
        )


class DialogBuilderTests(unittest.TestCase):
    def setUp(self) -> None:
        self.builder = (
            DialogBuilder()
            .title("Dialog Title")
            .callback_id("function_123")
            .submit_label("SubmitDialog")
            .notify_on_cancel(True)
            .text_field(
                name="signature",
                label="Signature",
                optional=True,
                hint="Enter your signature",
            )
            .text_area(name="message", label="Message", hint="Enter message to broadcast")
            .conversation_selector(name="target", label="Choose Target")
        )

    def test_basic_methods(self):
        self.assertEqual(self.builder._title, "Dialog Title")
        self.assertEqual(self.builder._callback_id, "function_123")
        self.assertEqual(self.builder._submit_label, "SubmitDialog")
        self.assertTrue(self.builder._notify_on_cancel)

    def test_element_appending(self):
        text_field, text_area, dropdown = self.builder._elements

        self.assertEqual(text_field.type, "text")
        self.assertEqual(text_field.name, "signature")
        self.assertEqual(text_field.label, "Signature")
        self.assertTrue(text_field.optional)
        self.assertEqual(text_field.hint, "Enter your signature")

        self.assertEqual(text_area.type, "textarea")
        self.assertEqual(text_area.name, "message")
        self.assertEqual(text_area.label, "Message")
        self.assertEqual(text_area.hint, "Enter message to broadcast")

        self.assertEqual(dropdown.type, "select")
        self.assertEqual(dropdown.name, "target")
        self.assertEqual(dropdown.label, "Choose Target")
        self.assertEqual(dropdown.data_source, "conversations")

    def test_build_without_errors(self):
        valid = {
            "title": "Dialog Title",
            "callback_id": "function_123",
            "elements": [
                {
                    "hint": "Enter your signature",
                    "min_length": 0,
                    "label": "Signature",
                    "name": "signature",
                    "optional": True,
                    "max_length": 150,
                    "type": "text",
                },
                {
                    "hint": "Enter message to broadcast",
                    "min_length": 0,
                    "label": "Message",
                    "name": "message",
                    "optional": False,
                    "max_length": 3000,
                    "type": "textarea",
                },
                {
                    "type": "select",
                    "label": "Choose Target",
                    "name": "target",
                    "optional": False,
                    "data_source": "conversations",
                },
            ],
            "notify_on_cancel": True,
            "submit_label": "SubmitDialog",
        }

        self.assertDictEqual(self.builder.to_dict(), valid)

    def test_build_validation(self):
        empty_title = copy(self.builder)
        # noinspection PyTypeChecker
        empty_title.title(None)
        with self.assertRaises(SlackObjectFormationError):
            empty_title.to_dict()

        too_long_title = copy(self.builder)
        too_long_title.title(STRING_51_CHARS)
        with self.assertRaises(SlackObjectFormationError):
            too_long_title.to_dict()

        empty_callback = copy(self.builder)
        # noinspection PyTypeChecker
        empty_callback.callback_id(None)
        with self.assertRaises(SlackObjectFormationError):
            empty_callback.to_dict()

        empty_dialog = copy(self.builder)
        empty_dialog._elements = []
        with self.assertRaises(SlackObjectFormationError):
            empty_dialog.to_dict()

        overfull_dialog = copy(self.builder)
        for i in range(8):
            overfull_dialog.text_field(name=f"element {i}", label="overflow")
        with self.assertRaises(SlackObjectFormationError):
            overfull_dialog.to_dict()
