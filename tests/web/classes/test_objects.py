import unittest

from slack.errors import SlackObjectFormationError
from slack.web.classes import JsonObject, JsonValidator
from slack.web.classes.objects import (
    ChannelLink,
    ConfirmObject,
    DateLink,
    EveryoneLink,
    HereLink,
    Link,
    MarkdownTextObject,
    ObjectLink,
    Option,
    OptionGroup,
    PlainTextObject,
)
from . import STRING_301_CHARS, STRING_51_CHARS


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
        datelink = DateLink(
            date=self.epoch, date_format="{date_long}", fallback=f"{self.epoch}"
        )
        self.assertEqual(f"{datelink}", f"<{self.epoch}^{{date_long}}|{self.epoch}>")

    def test_with_url(self):
        datelink = DateLink(
            date=self.epoch,
            date_format="{date_long}",
            link="http://google.com",
            fallback=f"{self.epoch}",
        )
        self.assertEqual(
            f"{datelink}",
            f"<{self.epoch}^{{date_long}}^http://google.com|{self.epoch}>",
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
            PlainTextObject(text="some text").to_dict(),
            {"text": "some text", "type": "plain_text", "emoji": True},
        )

        self.assertDictEqual(
            PlainTextObject(text="some text", emoji=False).to_dict(),
            {"text": "some text", "emoji": False, "type": "plain_text"},
        )

    def test_from_string(self):
        plaintext = PlainTextObject(text="some text")
        self.assertDictEqual(
            plaintext.to_dict(), PlainTextObject.direct_from_string("some text")
        )


class MarkdownTextObjectTests(unittest.TestCase):
    def test_basic_json(self):
        self.assertDictEqual(
            MarkdownTextObject(text="some text").to_dict(),
            {"text": "some text", "type": "mrkdwn", "verbatim": False},
        )

        self.assertDictEqual(
            MarkdownTextObject(text="some text", verbatim=True).to_dict(),
            {"text": "some text", "verbatim": True, "type": "mrkdwn"},
        )

    def test_from_string(self):
        markdown = MarkdownTextObject(text="some text")
        self.assertDictEqual(
            markdown.to_dict(), MarkdownTextObject.direct_from_string("some text")
        )


class ConfirmObjectTests(unittest.TestCase):
    def test_basic_json(self):
        expected = {
            "confirm": {"emoji": True, "text": "Yes", "type": "plain_text"},
            "deny": {"emoji": True, "text": "No", "type": "plain_text"},
            "text": {"text": "are you sure?", "type": "mrkdwn", "verbatim": False},
            "title": {"emoji": True, "text": "some title", "type": "plain_text"},
        }
        simple_object = ConfirmObject(title="some title", text="are you sure?")
        self.assertDictEqual(simple_object.to_dict(), expected)
        self.assertDictEqual(simple_object.to_dict("block"), expected)
        self.assertDictEqual(
            simple_object.to_dict("action"),
            {
                "text": "are you sure?",
                "title": "some title",
                "ok_text": "Okay",
                "dismiss_text": "Cancel",
            },
        )

    def test_confirm_overrides(self):
        confirm = ConfirmObject(
            title="some title",
            text="are you sure?",
            confirm="I'm really sure",
            deny="Nevermind",
        )
        expected = {
            "confirm": {"emoji": True, "text": "I'm really sure", "type": "plain_text"},
            "deny": {"emoji": True, "text": "Nevermind", "type": "plain_text"},
            "text": {"text": "are you sure?", "type": "mrkdwn", "verbatim": False},
            "title": {"emoji": True, "text": "some title", "type": "plain_text"},
        }
        self.assertDictEqual(confirm.to_dict(), expected)
        self.assertDictEqual(confirm.to_dict("block"), expected)
        self.assertDictEqual(
            confirm.to_dict("action"),
            {
                "text": "are you sure?",
                "title": "some title",
                "ok_text": "I'm really sure",
                "dismiss_text": "Nevermind",
            },
        )

    def test_passing_text_objects(self):
        direct_construction = ConfirmObject(title="title", text="Are you sure?")

        mrkdwn = MarkdownTextObject(text="Are you sure?")

        preconstructed = ConfirmObject(title="title", text=mrkdwn)

        self.assertDictEqual(direct_construction.to_dict(), preconstructed.to_dict())

        plaintext = PlainTextObject(text="Are you sure?", emoji=False)

        passed_plaintext = ConfirmObject(title="title", text=plaintext)

        self.assertDictEqual(
            passed_plaintext.to_dict(),
            {
                "confirm": {"emoji": True, "text": "Yes", "type": "plain_text"},
                "deny": {"emoji": True, "text": "No", "type": "plain_text"},
                "text": {"emoji": False, "text": "Are you sure?", "type": "plain_text"},
                "title": {"emoji": True, "text": "title", "type": "plain_text"},
            },
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
            ConfirmObject(
                title="title", text="Are you sure?", confirm=STRING_51_CHARS
            ).to_dict()

    def test_deny_length(self):
        with self.assertRaises(SlackObjectFormationError):
            ConfirmObject(
                title="title", text="Are you sure?", deny=STRING_51_CHARS
            ).to_dict()


class OptionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.common = Option(label="an option", value="option_1")

    def test_block_style_json(self):
        expected = {
            "text": {"type": "plain_text", "text": "an option", "emoji": True},
            "value": "option_1",
        }
        self.assertDictEqual(self.common.to_dict("block"), expected)
        self.assertDictEqual(self.common.to_dict(), expected)

    def test_dialog_style_json(self):
        expected = {"label": "an option", "value": "option_1"}
        self.assertDictEqual(self.common.to_dict("dialog"), expected)

    def test_action_style_json(self):
        expected = {"text": "an option", "value": "option_1"}
        self.assertDictEqual(self.common.to_dict("action"), expected)

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


class OptionGroupTests(unittest.TestCase):
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
        self.assertDictEqual(self.common.to_dict("block"), expected)
        self.assertDictEqual(self.common.to_dict(), expected)

    def test_dialog_style_json(self):
        self.assertDictEqual(
            self.common.to_dict("dialog"),
            {
                "label": "an option",
                "options": [
                    {"label": "one", "value": "one"},
                    {"label": "two", "value": "two"},
                    {"label": "three", "value": "three"},
                ],
            },
        )

    def test_action_style_json(self):
        self.assertDictEqual(
            self.common.to_dict("action"),
            {
                "text": "an option",
                "options": [
                    {"text": "one", "value": "one"},
                    {"text": "two", "value": "two"},
                    {"text": "three", "value": "three"},
                ],
            },
        )

    def test_label_length(self):
        with self.assertRaises(SlackObjectFormationError):
            OptionGroup(label=STRING_301_CHARS, options=self.common_options).to_dict(
                "text"
            )

    def test_options_length(self):
        with self.assertRaises(SlackObjectFormationError):
            OptionGroup(
                label="option_group", options=self.common_options * 34
            ).to_dict("text")
