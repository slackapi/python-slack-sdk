import copy
import unittest
from typing import List, Optional, Union

from slack_sdk.errors import SlackObjectFormationError
from slack_sdk.models import JsonObject, JsonValidator
from slack_sdk.models.blocks import ConfirmObject, MarkdownTextObject, Option, OptionGroup, PlainTextObject
from slack_sdk.models.blocks.basic_components import FeedbackButtonObject, Workflow, WorkflowTrigger
from slack_sdk.models.messages import ChannelLink, DateLink, EveryoneLink, HereLink, Link, ObjectLink

from . import STRING_51_CHARS, STRING_301_CHARS


class SimpleJsonObject(JsonObject):
    attributes = {"some", "test", "keys"}

    def __init__(self):
        self.some = "this is"
        self.test = "a test"
        self.keys = "object"

    @JsonValidator("some validation message")
    def test_valid(self):
        return len(self.test) <= 10

    @JsonValidator("this should never fail")
    def always_valid_test(self):
        return True


class KeyValueObject(JsonObject):
    attributes = {"name", "value"}

    def __init__(
        self,
        *,
        name: Optional[str] = None,
        value: Optional[str] = None,
    ):
        self.name = name
        self.value = value


class NestedObject(JsonObject):
    attributes = {"initial", "options"}

    def __init__(
        self,
        *,
        initial: Union[dict, KeyValueObject],
        options: List[Union[dict, KeyValueObject]],
    ):
        self.initial = KeyValueObject(**initial) if isinstance(initial, dict) else initial
        self.options = [KeyValueObject(**o) if isinstance(o, dict) else o for o in options]


class JsonObjectTests(unittest.TestCase):
    def setUp(self) -> None:
        self.good_test_object = SimpleJsonObject()
        obj = SimpleJsonObject()
        obj.test = STRING_51_CHARS
        self.bad_test_object = obj

    def test_json_formation(self):
        self.assertDictEqual(
            self.good_test_object.to_dict(),
            {"some": "this is", "test": "a test", "keys": "object"},
        )

    def test_validate_json_fails(self):
        with self.assertRaises(SlackObjectFormationError):
            self.bad_test_object.validate_json()

    def test_to_dict_performs_validation(self):
        with self.assertRaises(SlackObjectFormationError):
            self.bad_test_object.to_dict()

    def test_get_non_null_attributes(self):
        expected = {"name": "something"}
        obj = KeyValueObject(name="something", value=None)
        obj2 = copy.deepcopy(obj)
        self.assertDictEqual(expected, obj.get_non_null_attributes())
        self.assertEqual(str(obj2), str(obj))

    def test_get_non_null_attributes_nested(self):
        expected = {
            "initial": {"name": "something"},
            "options": [
                {"name": "something"},
                {"name": "message", "value": "That's great!"},
            ],
        }
        obj1 = KeyValueObject(name="something", value=None)
        obj2 = KeyValueObject(name="message", value="That's great!")
        options = [obj1, obj2]
        nested = NestedObject(initial=obj1, options=options)

        self.assertEqual(type(obj1), KeyValueObject)
        self.assertTrue(hasattr(obj1, "value"))
        self.assertEqual(type(nested.initial), KeyValueObject)

        self.assertEqual(type(options[0]), KeyValueObject)
        self.assertTrue(hasattr(options[0], "value"))
        self.assertEqual(type(nested.options[0]), KeyValueObject)
        self.assertTrue(hasattr(nested.options[0], "value"))

        dict_value = nested.get_non_null_attributes()
        self.assertDictEqual(expected, dict_value)

        self.assertEqual(type(obj1), KeyValueObject)
        self.assertTrue(hasattr(obj1, "value"))
        self.assertEqual(type(nested.initial), KeyValueObject)

        self.assertEqual(type(options[0]), KeyValueObject)
        self.assertTrue(hasattr(options[0], "value"))
        self.assertEqual(type(nested.options[0]), KeyValueObject)
        self.assertTrue(hasattr(nested.options[0], "value"))

    def test_get_non_null_attributes_nested_2(self):
        expected = {
            "initial": {"name": "something"},
            "options": [
                {"name": "something"},
                {"name": "message", "value": "That's great!"},
            ],
        }
        nested = NestedObject(
            initial={"name": "something"},
            options=[
                {"name": "something"},
                {"name": "message", "value": "That's great!"},
            ],
        )
        self.assertDictEqual(expected, nested.get_non_null_attributes())

    def test_eq(self):
        obj1 = SimpleJsonObject()
        self.assertEqual(self.good_test_object, obj1)

        obj2 = SimpleJsonObject()
        obj2.test = "another"
        self.assertNotEqual(self.good_test_object, obj2)

        self.assertNotEqual(self.good_test_object, None)


class JsonValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.validator_instance = JsonValidator("message")
        self.class_instance = SimpleJsonObject()

    def test_isolated_class(self):
        def does_nothing():
            return False

        wrapped = self.validator_instance(does_nothing)

        # noinspection PyUnresolvedReferences
        self.assertTrue(wrapped.validator)

    def test_wrapped_class(self):
        for attribute in dir(self.class_instance):
            attr = getattr(self.class_instance, attribute, None)
            if attribute in ("test_valid", "always_valid_test"):
                self.assertTrue(attr.validator)
            else:
                with self.assertRaises(AttributeError):
                    # noinspection PyStatementEffect
                    attr.validator


class LinkTests(unittest.TestCase):
    def test_without_text(self):
        link = Link(url="http://google.com", text="")
        self.assertEqual(f"{link}", "<http://google.com>")

    def test_with_text(self):
        link = Link(url="http://google.com", text="google")
        self.assertEqual(f"{link}", "<http://google.com|google>")


class DateLinkTests(unittest.TestCase):
    def setUp(self) -> None:
        self.epoch = 1234567890

    def test_simple_formation(self):
        datelink = DateLink(date=self.epoch, date_format="{date_long}", fallback=f"{self.epoch}")
        self.assertEqual(f"{datelink}", f"<!date^{self.epoch}^{{date_long}}|{self.epoch}>")

    def test_with_url(self):
        datelink = DateLink(
            date=self.epoch,
            date_format="{date_long}",
            link="http://google.com",
            fallback=f"{self.epoch}",
        )
        self.assertEqual(
            f"{datelink}",
            f"<!date^{self.epoch}^{{date_long}}^http://google.com|{self.epoch}>",
        )


class ObjectLinkTests(unittest.TestCase):
    def test_channel(self):
        objlink = ObjectLink(object_id="C12345")
        self.assertEqual(f"{objlink}", "<#C12345>")

    def test_group_message(self):
        objlink = ObjectLink(object_id="G12345")
        self.assertEqual(f"{objlink}", "<#G12345>")

    def test_subteam_message(self):
        objlink = ObjectLink(object_id="S12345")
        self.assertEqual(f"{objlink}", "<!subteam^S12345>")

    def test_with_label(self):
        objlink = ObjectLink(object_id="C12345", text="abc")
        self.assertEqual(f"{objlink}", "<#C12345|abc>")

    def test_unknown_prefix(self):
        objlink = ObjectLink(object_id="Z12345")
        self.assertEqual(f"{objlink}", "<@Z12345>")


class SpecialLinkTests(unittest.TestCase):
    def test_channel_link(self):
        self.assertEqual(f"{ChannelLink()}", "<!channel|channel>")

    def test_here_link(self):
        self.assertEqual(f"{HereLink()}", "<!here|here>")

    def test_everyone_link(self):
        self.assertEqual(f"{EveryoneLink()}", "<!everyone|everyone>")


class PlainTextObjectTests(unittest.TestCase):
    def test_basic_json(self):
        self.assertDictEqual(
            {"text": "some text", "type": "plain_text"},
            PlainTextObject(text="some text").to_dict(),
        )

        self.assertDictEqual(
            {"text": "some text", "emoji": False, "type": "plain_text"},
            PlainTextObject(text="some text", emoji=False).to_dict(),
        )

    def test_from_string(self):
        plaintext = PlainTextObject(text="some text", emoji=True)
        self.assertDictEqual(plaintext.to_dict(), PlainTextObject.direct_from_string("some text"))


class MarkdownTextObjectTests(unittest.TestCase):
    def test_basic_json(self):
        self.assertDictEqual(
            {"text": "some text", "type": "mrkdwn"},
            MarkdownTextObject(text="some text").to_dict(),
        )

        self.assertDictEqual(
            {"text": "some text", "verbatim": True, "type": "mrkdwn"},
            MarkdownTextObject(text="some text", verbatim=True).to_dict(),
        )

    def test_from_string(self):
        markdown = MarkdownTextObject(text="some text")
        self.assertDictEqual(markdown.to_dict(), MarkdownTextObject.direct_from_string("some text"))


class ConfirmObjectTests(unittest.TestCase):
    def test_basic_json(self):
        expected = {
            "confirm": {"emoji": True, "text": "Yes", "type": "plain_text"},
            "deny": {"emoji": True, "text": "No", "type": "plain_text"},
            "text": {"text": "are you sure?", "type": "mrkdwn"},
            "title": {"emoji": True, "text": "some title", "type": "plain_text"},
        }
        simple_object = ConfirmObject(title="some title", text="are you sure?")
        self.assertDictEqual(expected, simple_object.to_dict())
        self.assertDictEqual(expected, simple_object.to_dict("block"))
        self.assertDictEqual(
            {
                "text": "are you sure?",
                "title": "some title",
                "ok_text": "Okay",
                "dismiss_text": "Cancel",
            },
            simple_object.to_dict("action"),
        )

    def test_confirm_overrides(self):
        confirm = ConfirmObject(
            title="some title",
            text="are you sure?",
            confirm="I'm really sure",
            deny="Nevermind",
        )
        expected = {
            "confirm": {"text": "I'm really sure", "type": "plain_text", "emoji": True},
            "deny": {"text": "Nevermind", "type": "plain_text", "emoji": True},
            "text": {"text": "are you sure?", "type": "mrkdwn"},
            "title": {"text": "some title", "type": "plain_text", "emoji": True},
        }
        self.assertDictEqual(expected, confirm.to_dict())
        self.assertDictEqual(expected, confirm.to_dict("block"))
        self.assertDictEqual(
            {
                "text": "are you sure?",
                "title": "some title",
                "ok_text": "I'm really sure",
                "dismiss_text": "Nevermind",
            },
            confirm.to_dict("action"),
        )

    def test_passing_text_objects(self):
        direct_construction = ConfirmObject(title="title", text="Are you sure?")

        mrkdwn = MarkdownTextObject(text="Are you sure?")

        preconstructed = ConfirmObject(title="title", text=mrkdwn)

        self.assertDictEqual(direct_construction.to_dict(), preconstructed.to_dict())

        plaintext = PlainTextObject(text="Are you sure?", emoji=False)

        passed_plaintext = ConfirmObject(title="title", text=plaintext)

        self.assertDictEqual(
            {
                "confirm": {"emoji": True, "text": "Yes", "type": "plain_text"},
                "deny": {"emoji": True, "text": "No", "type": "plain_text"},
                "text": {"emoji": False, "text": "Are you sure?", "type": "plain_text"},
                "title": {"emoji": True, "text": "title", "type": "plain_text"},
            },
            passed_plaintext.to_dict(),
        )

    def test_title_length(self):
        with self.assertRaises(SlackObjectFormationError):
            ConfirmObject(title=STRING_301_CHARS, text="Are you sure?").to_dict()

    def test_text_length(self):
        with self.assertRaises(SlackObjectFormationError):
            ConfirmObject(title="title", text=STRING_301_CHARS).to_dict()

    def test_text_length_with_object(self):
        with self.assertRaises(SlackObjectFormationError):
            plaintext = PlainTextObject(text=STRING_301_CHARS)
            ConfirmObject(title="title", text=plaintext).to_dict()

        with self.assertRaises(SlackObjectFormationError):
            markdown = MarkdownTextObject(text=STRING_301_CHARS)
            ConfirmObject(title="title", text=markdown).to_dict()

    def test_confirm_length(self):
        with self.assertRaises(SlackObjectFormationError):
            ConfirmObject(title="title", text="Are you sure?", confirm=STRING_51_CHARS).to_dict()

    def test_deny_length(self):
        with self.assertRaises(SlackObjectFormationError):
            ConfirmObject(title="title", text="Are you sure?", deny=STRING_51_CHARS).to_dict()


class FeedbackButtonObjectTests(unittest.TestCase):
    def test_basic_json(self):
        feedback_button = FeedbackButtonObject(text="+1", value="positive")
        expected = {"text": {"emoji": True, "text": "+1", "type": "plain_text"}, "value": "positive"}
        self.assertDictEqual(expected, feedback_button.to_dict())

    def test_with_accessibility_label(self):
        feedback_button = FeedbackButtonObject(text="+1", value="positive", accessibility_label="Positive feedback button")
        expected = {
            "text": {"emoji": True, "text": "+1", "type": "plain_text"},
            "value": "positive",
            "accessibility_label": "Positive feedback button",
        }
        self.assertDictEqual(expected, feedback_button.to_dict())

    def test_with_plain_text_object(self):
        text_obj = PlainTextObject(text="-1", emoji=False)
        feedback_button = FeedbackButtonObject(text=text_obj, value="negative")
        expected = {
            "text": {"emoji": False, "text": "-1", "type": "plain_text"},
            "value": "negative",
        }
        self.assertDictEqual(expected, feedback_button.to_dict())

    def test_text_length_validation(self):
        with self.assertRaises(SlackObjectFormationError):
            FeedbackButtonObject(text="a" * 76, value="test").to_dict()

    def test_value_length_validation(self):
        with self.assertRaises(SlackObjectFormationError):
            FeedbackButtonObject(text="+1", value="a" * 2001).to_dict()

    def test_parse_from_dict(self):
        data = {"text": "+1", "value": "positive", "accessibility_label": "Positive feedback"}
        parsed = FeedbackButtonObject.parse(data)
        self.assertIsInstance(parsed, FeedbackButtonObject)
        expected = {
            "text": {"emoji": True, "text": "+1", "type": "plain_text"},
            "value": "positive",
            "accessibility_label": "Positive feedback",
        }
        self.assertDictEqual(expected, parsed.to_dict())

    def test_parse_from_existing_object(self):
        original = FeedbackButtonObject(text="-1", value="negative")
        parsed = FeedbackButtonObject.parse(original)
        self.assertIs(original, parsed)

    def test_parse_none(self):
        self.assertIsNone(FeedbackButtonObject.parse(None))


class OptionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.common = Option(label="an option", value="option_1")

    def test_block_style_json(self):
        expected = {
            "text": {"type": "plain_text", "text": "an option", "emoji": True},
            "value": "option_1",
        }
        self.assertDictEqual(expected, self.common.to_dict("block"))
        self.assertDictEqual(expected, self.common.to_dict())

    def test_dialog_style_json(self):
        expected = {"label": "an option", "value": "option_1"}
        self.assertDictEqual(expected, self.common.to_dict("dialog"))

    def test_action_style_json(self):
        expected = {"text": "an option", "value": "option_1"}
        self.assertDictEqual(expected, self.common.to_dict("action"))

    def test_from_single_value(self):
        option = Option(label="option_1", value="option_1")
        self.assertDictEqual(
            option.to_dict("text"),
            option.from_single_value("option_1").to_dict("text"),
        )

    def test_label_length(self):
        with self.assertRaises(SlackObjectFormationError):
            Option(label=STRING_301_CHARS, value="option_1").to_dict("text")

    def test_value_length(self):
        with self.assertRaises(SlackObjectFormationError):
            Option(label="option_1", value=STRING_301_CHARS).to_dict("text")

    def test_valid_description_for_blocks(self):
        option = Option(label="label", value="v", description="this is an option")
        self.assertDictEqual(
            option.to_dict(),
            {
                "text": {
                    "type": "plain_text",
                    "text": "label",
                    "emoji": True,
                },
                "value": "v",
                "description": {
                    "type": "plain_text",
                    "text": "this is an option",
                    "emoji": True,
                },
            },
        )
        option = Option(
            # Note that mrkdwn type is not allowed for this (as of April 2021)
            text=PlainTextObject(text="label"),
            value="v",
            description="this is an option",
        )
        self.assertDictEqual(
            option.to_dict(),
            {
                "text": {"type": "plain_text", "text": "label"},
                "value": "v",
                "description": {
                    "type": "plain_text",
                    "text": "this is an option",
                    "emoji": True,
                },
            },
        )

    def test_valid_description_for_attachments(self):
        option = Option(label="label", value="v", description="this is an option")
        # legacy message actions in attachments
        self.assertDictEqual(
            option.to_dict("action"),
            {
                "text": "label",
                "value": "v",
                "description": "this is an option",
            },
        )
        self.assertDictEqual(
            option.to_dict("attachment"),
            {
                "text": "label",
                "value": "v",
                "description": "this is an option",
            },
        )


class OptionGroupTests(unittest.TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.common_options = [
            Option.from_single_value("one"),
            Option.from_single_value("two"),
            Option.from_single_value("three"),
        ]

        self.common = OptionGroup(label="an option", options=self.common_options)

    def test_block_style_json(self):
        expected = {
            "label": {"emoji": True, "text": "an option", "type": "plain_text"},
            "options": [
                {
                    "text": {"emoji": True, "text": "one", "type": "plain_text"},
                    "value": "one",
                },
                {
                    "text": {"emoji": True, "text": "two", "type": "plain_text"},
                    "value": "two",
                },
                {
                    "text": {"emoji": True, "text": "three", "type": "plain_text"},
                    "value": "three",
                },
            ],
        }
        self.assertDictEqual(expected, self.common.to_dict("block"))
        self.assertDictEqual(expected, self.common.to_dict())

    def test_dialog_style_json(self):
        self.assertDictEqual(
            {
                "label": "an option",
                "options": [
                    {"label": "one", "value": "one"},
                    {"label": "two", "value": "two"},
                    {"label": "three", "value": "three"},
                ],
            },
            self.common.to_dict("dialog"),
        )

    def test_action_style_json(self):
        self.assertDictEqual(
            {
                "text": "an option",
                "options": [
                    {"text": "one", "value": "one"},
                    {"text": "two", "value": "two"},
                    {"text": "three", "value": "three"},
                ],
            },
            self.common.to_dict("action"),
        )

    def test_label_length(self):
        with self.assertRaises(SlackObjectFormationError):
            OptionGroup(label=STRING_301_CHARS, options=self.common_options).to_dict("text")

    def test_options_length(self):
        with self.assertRaises(SlackObjectFormationError):
            OptionGroup(label="option_group", options=self.common_options * 34).to_dict("text")

    def test_confirm_style(self):
        obj = ConfirmObject.parse(
            {
                "title": {"type": "plain_text", "text": "Are you sure?"},
                "text": {
                    "type": "mrkdwn",
                    "text": "Wouldn't you prefer a good game of _chess_?",
                },
                "confirm": {"type": "plain_text", "text": "Do it"},
                "deny": {"type": "plain_text", "text": "Stop, I've changed my mind!"},
                "style": "primary",
            }
        )
        obj.validate_json()
        self.assertEqual("primary", obj.style)

    def test_confirm_style_validation(self):
        with self.assertRaises(SlackObjectFormationError):
            ConfirmObject.parse(
                {
                    "title": {"type": "plain_text", "text": "Are you sure?"},
                    "text": {
                        "type": "mrkdwn",
                        "text": "Wouldn't you prefer a good game of _chess_?",
                    },
                    "confirm": {"type": "plain_text", "text": "Do it"},
                    "deny": {
                        "type": "plain_text",
                        "text": "Stop, I've changed my mind!",
                    },
                    "style": "something-wrong",
                }
            ).validate_json()


class WorkflowTests(unittest.TestCase):
    def test_creation(self):
        workflow = Workflow(
            trigger=WorkflowTrigger(
                url="https://slack.com/shortcuts/Ft0123ABC456/xyz...zyx",
                customizable_input_parameters=[
                    {"name": "input_parameter_a", "value": "Value for input param A"},
                    {"name": "input_parameter_b", "value": "Value for input param B"},
                ],
            )
        )
        self.assertDictEqual(
            workflow.to_dict(),
            {
                "trigger": {
                    "url": "https://slack.com/shortcuts/Ft0123ABC456/xyz...zyx",
                    "customizable_input_parameters": [
                        {"name": "input_parameter_a", "value": "Value for input param A"},
                        {"name": "input_parameter_b", "value": "Value for input param B"},
                    ],
                }
            },
        )
