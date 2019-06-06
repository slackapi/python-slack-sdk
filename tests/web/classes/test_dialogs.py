import unittest

from slack.web.classes.dialogs import (
    DialogSubTypes,
    DialogTextAreaComponent,
    DialogTextFieldComponent,
    StaticDialogDropdown,
)
from slack.web.classes.objects import SimpleOption
from . import STRING_3001_CHARS, STRING_301_CHARS, STRING_51_CHARS


class TextComponentTests(unittest.TestCase):
    def test_common_validation(self):
        for component in {DialogTextFieldComponent, DialogTextAreaComponent}:
            with self.assertRaises(AssertionError):
                with self.subTest("Long name", component=component):
                    component(STRING_301_CHARS, "label ")

                with self.subTest("Long label", component=component):
                    component("dialog", STRING_51_CHARS)

                with self.subTest("Long placeholder", component=component):
                    component("dialog", "Dialog", placeholder=STRING_301_CHARS)

                with self.subTest("Long hint", component=component):
                    component("dialog", "Dialog", hint=STRING_301_CHARS)

                with self.subTest("Long value", component=component):
                    component("dialog", "Dialog", value=STRING_3001_CHARS)

    def test_length_assertions(self):
        for component in {DialogTextFieldComponent, DialogTextAreaComponent}:
            with self.subTest(component=component):
                with self.assertRaises(AssertionError):
                    component(
                        "dialog", "Dialog", min_length=component.max_value_length + 100
                    )
                    component("dialog", "Dialog", max_length=component.max_value_length)
                    component("dialog", "Dialog", min_length=100, max_length=50)

    def test_subtypes(self):
        for component in {DialogTextFieldComponent, DialogTextAreaComponent}:
            for subtype in DialogSubTypes:
                with self.subTest(component=component, type=subtype):
                    self.assertEqual(
                        subtype.value,
                        component("dialog", "Dialog", subtype=subtype).get_json()[
                            "subtype"
                        ],
                    )
                    self.assertEqual(
                        subtype.value,
                        component("dialog", "Dialog", subtype=subtype.value).get_json()[
                            "subtype"
                        ],
                    )

            with self.assertRaises(AssertionError):
                with self.subTest(component=component):
                    component("dialog", "Dialog", subtype="abcdefg")


class TextFieldComponentTests(unittest.TestCase):
    def test_basic_json_formation(self):
        tf = DialogTextFieldComponent("dialog", "Dialog")

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
            "dialog",
            "Dialog",
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
        ta = DialogTextAreaComponent("dialog", "Dialog")

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
            "dialog",
            "Dialog",
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
        options = [SimpleOption("one"), SimpleOption("two"), SimpleOption("three")]
        dd = StaticDialogDropdown("dialog", "Dialog", options)

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
