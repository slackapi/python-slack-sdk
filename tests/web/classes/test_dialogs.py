import unittest
from copy import copy

from slack.errors import SlackObjectFormationError
from slack.web.classes.dialogs import (
    DialogBuilder,
    DialogTextAreaComponent,
    DialogTextFieldComponent,
    StaticDialogDropdown,
)
from slack.web.classes.objects import SimpleOption
from . import STRING_3001_CHARS, STRING_301_CHARS, STRING_51_CHARS


class TextComponentTests(unittest.TestCase):
    def test_common_validation(self):
        for component in {DialogTextFieldComponent, DialogTextAreaComponent}:
            with self.assertRaises(SlackObjectFormationError):
                with self.subTest("Long name", component=component):
                    component(name=STRING_301_CHARS, label="label ").get_json()

                with self.subTest("Long label", component=component):
                    component(name="dialog", label=STRING_51_CHARS).get_json()

                with self.subTest("Long placeholder", component=component):
                    component(
                        name="dialog", label="Dialog", placeholder=STRING_301_CHARS
                    ).get_json()

                with self.subTest("Long hint", component=component):
                    component(
                        name="dialog", label="Dialog", hint=STRING_301_CHARS
                    ).get_json()

                with self.subTest("Long value", component=component):
                    component(
                        name="dialog", label="Dialog", value=STRING_3001_CHARS
                    ).get_json()

    def test_length_assertions(self):
        for component in {DialogTextFieldComponent, DialogTextAreaComponent}:
            with self.subTest(component=component):
                with self.assertRaises(
                    SlackObjectFormationError, msg="Excessive min length"
                ):
                    component(
                        name="dialog",
                        label="Dialog",
                        min_length=component.max_value_length + 1,
                    ).get_json()
                with self.assertRaises(
                    SlackObjectFormationError, msg="Excessive max length"
                ):
                    component(
                        name="dialog",
                        label="Dialog",
                        max_length=component.max_value_length + 1,
                    ).get_json()
                with self.assertRaises(
                    SlackObjectFormationError, msg="Min > max length"
                ):
                    component(
                        name="dialog", label="Dialog", min_length=100, max_length=50
                    ).get_json()

    def test_subtypes(self):
        for component in {DialogTextFieldComponent, DialogTextAreaComponent}:
            with self.assertRaises(SlackObjectFormationError):
                with self.subTest(component=component):
                    component(
                        name="dialog", label="Dialog", subtype="abcdefg"
                    ).get_json()


class TextFieldComponentTests(unittest.TestCase):
    def test_basic_json_formation(self):
        tf = DialogTextFieldComponent(name="dialog", label="Dialog")

        e = {
            "min_length": 0,
            "max_length": 150,
            "name": "dialog",
            "optional": False,
            "label": "Dialog",
            "type": "text",
        }

        self.assertDictEqual(tf.get_json(), e)

    def test_complex_json_formation(self):
        ta = DialogTextFieldComponent(
            name="dialog",
            label="Dialog",
            optional=True,
            hint="Some hint",
            max_length=100,
            min_length=20,
        )

        e = {
            "min_length": 20,
            "max_length": 100,
            "name": "dialog",
            "optional": True,
            "label": "Dialog",
            "type": "text",
            "hint": "Some hint",
        }

        self.assertDictEqual(ta.get_json(), e)


class TextAreaComponentTests(unittest.TestCase):
    def test_basic_json_formation(self):
        ta = DialogTextAreaComponent(name="dialog", label="Dialog")

        e = {
            "min_length": 0,
            "max_length": 3000,
            "name": "dialog",
            "optional": False,
            "label": "Dialog",
            "type": "textarea",
        }

        self.assertDictEqual(ta.get_json(), e)

    def test_complex_json_formation(self):
        ta = DialogTextAreaComponent(
            name="dialog",
            label="Dialog",
            optional=True,
            hint="Some hint",
            max_length=500,
            min_length=100,
        )

        e = {
            "min_length": 100,
            "max_length": 500,
            "name": "dialog",
            "optional": True,
            "label": "Dialog",
            "type": "textarea",
            "hint": "Some hint",
        }

        self.assertDictEqual(ta.get_json(), e)


class StaticDropdownTests(unittest.TestCase):
    def test_basic_json_formation(self):
        options = [
            SimpleOption(label="one"),
            SimpleOption(label="two"),
            SimpleOption(label="three"),
        ]
        dd = StaticDialogDropdown(name="dialog", label="Dialog", options=options)

        e = {
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
        }

        self.assertDictEqual(dd.get_json(), e)


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
            .text_area(
                name="message", label="Message", hint="Enter message to broadcast"
            )
            .auto_dropdown(name="target", label="Choose Target", source="conversations")
        )

    def test_basic_methods(self):
        self.assertEqual(self.builder._title, "Dialog Title")
        self.assertEqual(self.builder._callback_id, "function_123")
        self.assertEqual(self.builder._submit_label, "SubmitDialog")
        self.assertTrue(self.builder._notify_on_cancel)

    def test_element_appending(self):
        text_field, text_area, dropdown = self.builder._elements

        self.assertEqual(text_field.element_type, "text")
        self.assertEqual(text_field.name, "signature")
        self.assertEqual(text_field.label, "Signature")
        self.assertTrue(text_field.optional)
        self.assertEqual(text_field.hint, "Enter your signature")

        self.assertEqual(text_area.element_type, "textarea")
        self.assertEqual(text_area.name, "message")
        self.assertEqual(text_area.label, "Message")
        self.assertEqual(text_area.hint, "Enter message to broadcast")

        self.assertEqual(dropdown.type, "select")
        self.assertEqual(dropdown.name, "target")
        self.assertEqual(dropdown.label, "Choose Target")
        self.assertEqual(dropdown.source, "conversations")

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

        self.assertDictEqual(self.builder.build(), valid)

    def test_build_validation(self):
        empty_title = copy(self.builder)
        empty_title.title(None)
        with self.assertRaises(SlackObjectFormationError):
            empty_title.build()

        too_long_title = copy(self.builder)
        too_long_title.title(STRING_51_CHARS)
        with self.assertRaises(SlackObjectFormationError):
            too_long_title.build()

        empty_callback = copy(self.builder)
        empty_callback.callback_id(None)
        with self.assertRaises(SlackObjectFormationError):
            empty_callback.build()

        empty_dialog = copy(self.builder)
        empty_dialog._elements = []
        with self.assertRaises(SlackObjectFormationError):
            empty_dialog.build()

        overfull_dialog = copy(self.builder)
        for i in range(8):
            overfull_dialog.text_field(name=f"element {i}", label="overflow")
        with self.assertRaises(SlackObjectFormationError):
            overfull_dialog.build()
