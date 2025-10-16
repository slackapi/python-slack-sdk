import unittest
from typing import List

from slack_sdk.errors import SlackObjectFormationError
from slack_sdk.models.blocks import (
    ActionsBlock,
    Block,
    ButtonElement,
    CallBlock,
    ContextActionsBlock,
    ContextBlock,
    DividerBlock,
    FileBlock,
    HeaderBlock,
    ImageBlock,
    ImageElement,
    InputBlock,
    LinkButtonElement,
    MarkdownBlock,
    MarkdownTextObject,
    Option,
    OverflowMenuElement,
    PlainTextObject,
    RichTextBlock,
    RichTextElementParts,
    RichTextListElement,
    RichTextPreformattedElement,
    RichTextQuoteElement,
    RichTextSectionElement,
    SectionBlock,
    StaticSelectElement,
    VideoBlock,
)
from slack_sdk.models.blocks.basic_components import FeedbackButtonObject, SlackFile
from slack_sdk.models.blocks.block_elements import FeedbackButtonsElement, IconButtonElement

from . import STRING_3001_CHARS

# https://docs.slack.dev/reference/block-kit/blocks


class BlockTests(unittest.TestCase):
    def test_parse(self):
        input = {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "A message *with some bold text* and _some italicized text_.",
            },
            "unexpected_field": "test",
            "unexpected_fields": [1, 2, 3],
            "unexpected_object": {"something": "wrong"},
        }
        block = Block.parse(input)
        self.assertIsNotNone(block)

        self.assertDictEqual(
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "A message *with some bold text* and _some italicized text_.",
                },
            },
            block.to_dict(),
        )

    def test_eq(self):
        self.assertEqual(Block(), Block())
        self.assertEqual(Block(type="test"), Block(type="test"))
        self.assertNotEqual(Block(type="test"), Block(type="another test"))


# ----------------------------------------------
# Section
# ----------------------------------------------


class SectionBlockTests(unittest.TestCase):
    maxDiff = None

    def test_document_1(self):
        input = {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "A message *with some bold text* and _some italicized text_.",
            },
        }
        self.assertDictEqual(input, SectionBlock(**input).to_dict())

    def test_document_2(self):
        input = {
            "type": "section",
            "text": {
                "text": "A message *with some bold text* and _some italicized text_.",
                "type": "mrkdwn",
            },
            "fields": [
                {"type": "mrkdwn", "text": "High"},
                {"type": "plain_text", "emoji": True, "text": "String"},
            ],
        }
        self.assertDictEqual(input, SectionBlock(**input).to_dict())

    def test_document_3(self):
        input = {
            "type": "section",
            "text": {
                "text": "*Sally* has requested you set the deadline for the Nano launch project",
                "type": "mrkdwn",
            },
            "accessory": {
                "type": "datepicker",
                "action_id": "datepicker123",
                "initial_date": "1990-04-28",
                "placeholder": {"type": "plain_text", "text": "Select a date"},
            },
        }
        self.assertDictEqual(input, SectionBlock(**input).to_dict())

    def test_parse(self):
        input = {
            "type": "section",
            "text": {
                "type": "plain_text",
                "text": "This is a plain text section block.",
                "emoji": True,
            },
        }
        self.assertDictEqual(input, SectionBlock(**input).to_dict())

    def test_parse_2(self):
        input = {
            "type": "section",
            "text": {
                "type": "plain_text",
                "text": "This is a plain text section block.",
                "emoji": True,
            },
            "expand": True,
        }
        self.assertDictEqual(input, SectionBlock(**input).to_dict())

    def test_json(self):
        self.assertDictEqual(
            {
                "text": {"text": "some text", "type": "mrkdwn"},
                "block_id": "a_block",
                "type": "section",
            },
            SectionBlock(text="some text", block_id="a_block").to_dict(),
        )

        self.assertDictEqual(
            {
                "text": {"text": "some text", "type": "mrkdwn"},
                "fields": [
                    {"text": "field0", "type": "mrkdwn"},
                    {"text": "field1", "type": "mrkdwn"},
                    {"text": "field2", "type": "mrkdwn"},
                    {"text": "field3", "type": "mrkdwn"},
                    {"text": "field4", "type": "mrkdwn"},
                ],
                "type": "section",
            },
            SectionBlock(text="some text", fields=[f"field{i}" for i in range(5)]).to_dict(),
        )

        button = LinkButtonElement(text="Click me!", url="https://example.com")
        self.assertDictEqual(
            {
                "type": "section",
                "text": {"text": "some text", "type": "mrkdwn"},
                "accessory": button.to_dict(),
            },
            SectionBlock(text="some text", accessory=button).to_dict(),
        )

    def test_text_or_fields_populated(self):
        with self.assertRaises(SlackObjectFormationError):
            SectionBlock().to_dict()

    def test_fields_length(self):
        with self.assertRaises(SlackObjectFormationError):
            SectionBlock(fields=[f"field{i}" for i in range(11)]).to_dict()

    def test_issue_628(self):
        elem = SectionBlock(text="1234567890" * 300)
        elem.to_dict()  # no exception
        with self.assertRaises(SlackObjectFormationError):
            elem = SectionBlock(text="1234567890" * 300 + "a")
            elem.to_dict()

    @classmethod
    def build_slack_block(cls, msg1, msg2, data):
        blocks = [
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*{msg1}*:\n{msg2}"},
            },
            {"type": "section", "fields": []},
        ]
        names = list(set(data.keys()) - set("user_comments"))
        fields = [{"type": "mrkdwn", "text": f"*{name}*:\n{data[name]}"} for name in names]
        blocks[1]["fields"] = fields
        return blocks

    @classmethod
    def build_slack_block_native(cls, msg1, msg2, data):
        blocks: List[SectionBlock] = [
            SectionBlock(text=MarkdownTextObject.parse(f"*{msg1}*:\n{msg2}")),
            SectionBlock(fields=[]),
        ]
        names: List[str] = list(set(data.keys()) - set("user_comments"))
        fields = [MarkdownTextObject.parse(f"*{name}*:\n{data[name]}") for name in names]
        blocks[1].fields = fields
        return list(b.to_dict() for b in blocks)

    def test_issue_500(self):
        data = {
            "first": "1",
            "second": "2",
            "third": "3",
            "user_comments": {"first", "other"},
        }
        expected = self.build_slack_block("category", "tech", data)
        actual = self.build_slack_block_native("category", "tech", data)
        self.assertDictEqual({"blocks": expected}, {"blocks": actual})


# ----------------------------------------------
# Divider
# ----------------------------------------------


class DividerBlockTests(unittest.TestCase):
    def test_document(self):
        input = {"type": "divider"}
        self.assertDictEqual(input, DividerBlock(**input).to_dict())

    def test_json(self):
        self.assertDictEqual({"type": "divider"}, DividerBlock().to_dict())
        self.assertDictEqual({"type": "divider"}, DividerBlock(**{"type": "divider"}).to_dict())

    def test_json_with_block_id(self):
        self.assertDictEqual(
            {"type": "divider", "block_id": "foo"},
            DividerBlock(block_id="foo").to_dict(),
        )
        self.assertDictEqual(
            {"type": "divider", "block_id": "foo"},
            DividerBlock(**{"type": "divider", "block_id": "foo"}).to_dict(),
        )


# ----------------------------------------------
# Image
# ----------------------------------------------


class ImageBlockTests(unittest.TestCase):
    def test_document(self):
        input = {
            "type": "image",
            "title": {
                "type": "plain_text",
                "text": "Please enjoy this photo of a kitten",
            },
            "block_id": "image4",
            "image_url": "http://placekitten.com/500/500",
            "alt_text": "An incredibly cute kitten.",
        }
        self.assertDictEqual(input, ImageBlock(**input).to_dict())

    def test_issue_1369_title_type(self):
        self.assertEqual(
            "plain_text",
            ImageBlock(
                image_url="https://example.com/",
                alt_text="example",
                title="example",
            ).title.type,
        )

        self.assertEqual(
            "plain_text",
            ImageBlock(
                image_url="https://example.com/",
                alt_text="example",
                title={
                    "type": "plain_text",
                    "text": "Please enjoy this photo of a kitten",
                },
            ).title.type,
        )

        self.assertEqual(
            "plain_text",
            ImageBlock(
                image_url="https://example.com/",
                alt_text="example",
                title=PlainTextObject(text="example"),
            ).title.type,
        )

        with self.assertRaises(SlackObjectFormationError):
            self.assertEqual(
                "plain_text",
                ImageBlock(
                    image_url="https://example.com/",
                    alt_text="example",
                    title={
                        "type": "mrkdwn",
                        "text": "Please enjoy this photo of a kitten",
                    },
                ).title.type,
            )

            with self.assertRaises(SlackObjectFormationError):
                self.assertEqual(
                    "plain_text",
                    ImageBlock(
                        image_url="https://example.com/",
                        alt_text="example",
                        title=MarkdownTextObject(text="example"),
                    ).title.type,
                )

    def test_json(self):
        self.assertDictEqual(
            {
                "image_url": "https://example.com",
                "alt_text": "not really an image",
                "type": "image",
            },
            ImageBlock(image_url="https://example.com", alt_text="not really an image").to_dict(),
        )

    def test_image_url_length(self):
        with self.assertRaises(SlackObjectFormationError):
            ImageBlock(image_url=STRING_3001_CHARS, alt_text="text").to_dict()

    def test_alt_text_length(self):
        with self.assertRaises(SlackObjectFormationError):
            ImageBlock(image_url="https://example.com", alt_text=STRING_3001_CHARS).to_dict()

    def test_title_length(self):
        with self.assertRaises(SlackObjectFormationError):
            ImageBlock(image_url="https://example.com", alt_text="text", title=STRING_3001_CHARS).to_dict()

    def test_slack_file(self):
        self.assertDictEqual(
            {
                "slack_file": {"url": "https://example.com"},
                "alt_text": "not really an image",
                "type": "image",
            },
            ImageBlock(slack_file=SlackFile(url="https://example.com"), alt_text="not really an image").to_dict(),
        )
        self.assertDictEqual(
            {
                "slack_file": {"id": "F11111"},
                "alt_text": "not really an image",
                "type": "image",
            },
            ImageBlock(slack_file=SlackFile(id="F11111"), alt_text="not really an image").to_dict(),
        )
        self.assertDictEqual(
            {
                "slack_file": {"url": "https://example.com"},
                "alt_text": "not really an image",
                "type": "image",
            },
            ImageBlock(slack_file={"url": "https://example.com"}, alt_text="not really an image").to_dict(),
        )
        self.assertDictEqual(
            {
                "slack_file": {"id": "F11111"},
                "alt_text": "not really an image",
                "type": "image",
            },
            ImageBlock(slack_file={"id": "F11111"}, alt_text="not really an image").to_dict(),
        )


# ----------------------------------------------
# Actions
# ----------------------------------------------


class ActionsBlockTests(unittest.TestCase):
    def test_document_1(self):
        input = {
            "type": "actions",
            "block_id": "actions1",
            "elements": [
                {
                    "type": "static_select",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Which witch is the witchiest witch?",
                    },
                    "action_id": "select_2",
                    "options": [
                        {
                            "text": {"type": "plain_text", "text": "Matilda"},
                            "value": "matilda",
                        },
                        {
                            "text": {"type": "plain_text", "text": "Glinda"},
                            "value": "glinda",
                        },
                        {
                            "text": {"type": "plain_text", "text": "Granny Weatherwax"},
                            "value": "grannyWeatherwax",
                        },
                        {
                            "text": {"type": "plain_text", "text": "Hermione"},
                            "value": "hermione",
                        },
                    ],
                },
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Cancel"},
                    "value": "cancel",
                    "action_id": "button_1",
                },
            ],
        }
        self.assertDictEqual(input, ActionsBlock(**input).to_dict())

    def test_document_2(self):
        input = {
            "type": "actions",
            "block_id": "actionblock789",
            "elements": [
                {
                    "type": "datepicker",
                    "action_id": "datepicker123",
                    "initial_date": "1990-04-28",
                    "placeholder": {"type": "plain_text", "text": "Select a date"},
                },
                {
                    "type": "overflow",
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
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "*this is plain_text text*",
                            },
                            "value": "value-3",
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "*this is plain_text text*",
                            },
                            "value": "value-4",
                        },
                    ],
                    "action_id": "overflow",
                },
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Click Me"},
                    "value": "click_me_123",
                    "action_id": "button",
                },
            ],
        }
        self.assertDictEqual(input, ActionsBlock(**input).to_dict())

    def test_json(self):
        self.elements = [
            ButtonElement(text="Click me", action_id="reg_button", value="1"),
            LinkButtonElement(text="URL Button", url="https://example.com"),
        ]
        self.dict_elements = []
        for e in self.elements:
            self.dict_elements.append(e.to_dict())

        self.assertDictEqual(
            {"elements": self.dict_elements, "type": "actions"},
            ActionsBlock(elements=self.elements).to_dict(),
        )
        with self.assertRaises(SlackObjectFormationError):
            ActionsBlock(elements=self.elements * 13).to_dict()

    def test_element_parsing(self):
        elements = [
            ButtonElement(text="Click me", action_id="reg_button", value="1"),
            StaticSelectElement(options=[Option(value="SelectOption")]),
            ImageElement(image_url="url", alt_text="alt-text"),
            OverflowMenuElement(options=[Option(value="MenuOption1"), Option(value="MenuOption2")]),
        ]
        input = {
            "type": "actions",
            "block_id": "actionblock789",
            "elements": [e.to_dict() for e in elements],
        }
        parsed_elements = ActionsBlock(**input).elements
        self.assertEqual(len(elements), len(parsed_elements))
        for original, parsed in zip(elements, parsed_elements):
            self.assertEqual(type(original), type(parsed))
            self.assertDictEqual(original.to_dict(), parsed.to_dict())


# ----------------------------------------------
# ContextActionsBlock
# ----------------------------------------------


class ContextActionsBlockTests(unittest.TestCase):
    def test_document(self):
        input = {
            "type": "context_actions",
            "block_id": "context-actions-1",
            "elements": [
                {
                    "type": "feedback_buttons",
                    "action_id": "feedback-action",
                    "positive_button": {"text": {"type": "plain_text", "text": "+1"}, "value": "positive"},
                    "negative_button": {"text": {"type": "plain_text", "text": "-1"}, "value": "negative"},
                },
                {
                    "type": "icon_button",
                    "action_id": "delete-action",
                    "icon": "trash",
                    "text": {"type": "plain_text", "text": "Delete"},
                    "value": "delete",
                },
            ],
        }
        self.assertDictEqual(input, ContextActionsBlock(**input).to_dict())
        self.assertDictEqual(input, Block.parse(input).to_dict())

    def test_with_feedback_buttons(self):
        feedback_buttons = FeedbackButtonsElement(
            action_id="feedback-action",
            positive_button=FeedbackButtonObject(text="Good", value="positive"),
            negative_button=FeedbackButtonObject(text="Bad", value="negative"),
        )
        block = ContextActionsBlock(elements=[feedback_buttons])
        self.assertEqual(len(block.elements), 1)
        self.assertEqual(block.elements[0].type, "feedback_buttons")

    def test_with_icon_button(self):
        icon_button = IconButtonElement(
            action_id="icon-action", icon="star", text=PlainTextObject(text="Favorite"), value="favorite"
        )
        block = ContextActionsBlock(elements=[icon_button])
        self.assertEqual(len(block.elements), 1)
        self.assertEqual(block.elements[0].type, "icon_button")


# ----------------------------------------------
# Context
# ----------------------------------------------


class ContextBlockTests(unittest.TestCase):
    def test_document(self):
        input = {
            "type": "context",
            "elements": [
                {
                    "type": "image",
                    "image_url": "https://image.freepik.com/free-photo/red-drawing-pin_1156-445.jpg",
                    "alt_text": "images",
                },
                {"type": "mrkdwn", "text": "Location: **Dogpatch**"},
            ],
        }
        self.assertDictEqual(input, ContextBlock(**input).to_dict())

    def test_basic_json(self):
        self.elements = [
            ImageElement(
                image_url="https://api.slack.com/img/blocks/bkb_template_images/palmtree.png",
                alt_text="palmtree",
            ),
            PlainTextObject(text="Just text"),
        ]
        e = {
            "elements": [
                {
                    "type": "image",
                    "image_url": "https://api.slack.com/img/blocks/bkb_template_images/palmtree.png",
                    "alt_text": "palmtree",
                },
                {"type": "plain_text", "text": "Just text"},
            ],
            "type": "context",
        }
        d = ContextBlock(elements=self.elements).to_dict()
        self.assertDictEqual(e, d)

        with self.assertRaises(SlackObjectFormationError):
            ContextBlock(elements=self.elements * 6).to_dict()


# ----------------------------------------------
# Input
# ----------------------------------------------


class InputBlockTests(unittest.TestCase):
    def test_document(self):
        blocks = [
            {
                "type": "input",
                "element": {"type": "plain_text_input"},
                "label": {"type": "plain_text", "text": "Label", "emoji": True},
            },
            {
                "type": "input",
                "element": {"type": "plain_text_input", "multiline": True},
                "label": {"type": "plain_text", "text": "Label", "emoji": True},
            },
            {
                "type": "input",
                "element": {
                    "type": "datepicker",
                    "initial_date": "1990-04-28",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select a date",
                        "emoji": True,
                    },
                },
                "label": {"type": "plain_text", "text": "Label", "emoji": True},
            },
            {
                "type": "input",
                "element": {
                    "type": "channels_select",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select a channel",
                        "emoji": True,
                    },
                },
                "label": {"type": "plain_text", "text": "Label", "emoji": True},
            },
            {
                "type": "input",
                "element": {
                    "type": "multi_users_select",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select users",
                        "emoji": True,
                    },
                },
                "label": {"type": "plain_text", "text": "Label", "emoji": True},
            },
            {
                "type": "input",
                "element": {
                    "type": "checkboxes",
                    "options": [
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "*this is plain_text text*",
                                "emoji": True,
                            },
                            "value": "value-0",
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "*this is plain_text text*",
                                "emoji": True,
                            },
                            "value": "value-1",
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "*this is plain_text text*",
                                "emoji": True,
                            },
                            "value": "value-2",
                        },
                    ],
                },
                "label": {"type": "plain_text", "text": "Label", "emoji": True},
            },
            {
                "type": "input",
                "element": {
                    "type": "plain_text_input",
                },
                "label": {
                    "type": "plain_text",
                    "text": "Label",
                    "emoji": True,
                },
                "hint": {
                    "type": "plain_text",
                    "text": "some hint",
                    "emoji": True,
                },
            },
            {
                "dispatch_action": True,
                "type": "input",
                "element": {
                    "type": "plain_text_input",
                    "action_id": "plain_text_input-action",
                },
                "label": {"type": "plain_text", "text": "Label", "emoji": True},
            },
        ]
        for input in blocks:
            self.assertDictEqual(input, InputBlock(**input).to_dict())


# ----------------------------------------------
# File
# ----------------------------------------------


class FileBlockTests(unittest.TestCase):
    def test_document(self):
        input = {
            "type": "file",
            "external_id": "ABCD1",
            "source": "remote",
        }
        self.assertDictEqual(input, FileBlock(**input).to_dict())


# ----------------------------------------------
# Call
# ----------------------------------------------


class CallBlockTests(unittest.TestCase):
    def test_with_real_payload(self):
        self.maxDiff = None
        input = {
            "type": "call",
            "call_id": "R00000000",
            "api_decoration_available": False,
            "call": {
                "v1": {
                    "id": "R00000000",
                    "app_id": "A00000000",
                    "app_icon_urls": {
                        "image_32": "https://www.example.com/",
                        "image_36": "https://www.example.com/",
                        "image_48": "https://www.example.com/",
                        "image_64": "https://www.example.com/",
                        "image_72": "https://www.example.com/",
                        "image_96": "https://www.example.com/",
                        "image_128": "https://www.example.com/",
                        "image_192": "https://www.example.com/",
                        "image_512": "https://www.example.com/",
                        "image_1024": "https://www.example.com/",
                        "image_original": "https://www.example.com/",
                    },
                    "date_start": 12345,
                    "active_participants": [
                        {"slack_id": "U00000000"},
                        {
                            "slack_id": "U00000000",
                            "external_id": "",
                            "avatar_url": "https://www.example.com/",
                            "display_name": "",
                        },
                    ],
                    "all_participants": [
                        {"slack_id": "U00000000"},
                        {
                            "slack_id": "U00000000",
                            "external_id": "",
                            "avatar_url": "https://www.example.com/",
                            "display_name": "",
                        },
                    ],
                    "display_id": "",
                    "join_url": "https://www.example.com/",
                    "name": "",
                    "created_by": "U00000000",
                    "date_end": 12345,
                    "channels": ["C00000000"],
                    "is_dm_call": False,
                    "was_rejected": False,
                    "was_missed": False,
                    "was_accepted": False,
                    "has_ended": False,
                    "desktop_app_join_url": "https://www.example.com/",
                }
            },
        }
        self.assertDictEqual(input, CallBlock(**input).to_dict())
        self.assertDictEqual(input, Block.parse(input).to_dict())


# ----------------------------------------------
# Header
# ----------------------------------------------


class HeaderBlockTests(unittest.TestCase):
    def test_document(self):
        input = {
            "type": "header",
            "block_id": "budget-header",
            "text": {"type": "plain_text", "text": "Budget Performance"},
        }
        self.assertDictEqual(input, HeaderBlock(**input).to_dict())
        self.assertDictEqual(input, Block.parse(input).to_dict())

    def test_text_length_150(self):
        input = {
            "type": "header",
            "block_id": "budget-header",
            "text": {"type": "plain_text", "text": "1234567890" * 15},
        }
        HeaderBlock(**input).validate_json()

    def test_text_length_151(self):
        input = {
            "type": "header",
            "block_id": "budget-header",
            "text": {"type": "plain_text", "text": ("1234567890" * 15) + "1"},
        }
        with self.assertRaises(SlackObjectFormationError):
            HeaderBlock(**input).validate_json()


# ----------------------------------------------
# MarkdownBlock
# ----------------------------------------------


class MarkdownBlockTests(unittest.TestCase):
    def test_document(self):
        input = {
            "type": "markdown",
            "block_id": "introduction",
            "text": "**Welcome!**",
        }
        self.assertDictEqual(input, MarkdownBlock(**input).to_dict())
        self.assertDictEqual(input, Block.parse(input).to_dict())

    def test_text_length_12000(self):
        input = {
            "type": "markdown",
            "block_id": "numbers",
            "text": "1234567890" * 1200,
        }
        MarkdownBlock(**input).validate_json()

    def test_text_length_12001(self):
        input = {
            "type": "markdown",
            "block_id": "numbers",
            "text": "1234567890" * 1200 + "1",
        }
        with self.assertRaises(SlackObjectFormationError):
            MarkdownBlock(**input).validate_json()


# ----------------------------------------------
# Video
# ----------------------------------------------


class VideoBlockTests(unittest.TestCase):
    def test_document(self):
        input = {
            "type": "video",
            "title": {"type": "plain_text", "text": "How to use Slack.", "emoji": True},
            "title_url": "https://www.youtube.com/watch?v=RRxQQxiM7AA",
            "description": {
                "type": "plain_text",
                "text": "Slack is a new way to communicate with your team. "
                "It's faster, better organized and more secure than email.",
                "emoji": True,
            },
            "video_url": "https://www.youtube.com/embed/RRxQQxiM7AA?feature=oembed&autoplay=1",
            "alt_text": "How to use Slack?",
            "thumbnail_url": "https://i.ytimg.com/vi/RRxQQxiM7AA/hqdefault.jpg",
            "author_name": "Arcado Buendia",
            "provider_name": "YouTube",
            "provider_icon_url": "https://a.slack-edge.com/80588/img/unfurl_icons/youtube.png",
        }
        self.assertDictEqual(input, VideoBlock(**input).to_dict())
        self.assertDictEqual(input, Block.parse(input).to_dict())

    def test_required(self):
        input = {
            "type": "video",
            "title": {"type": "plain_text", "text": "How to use Slack.", "emoji": True},
            "video_url": "https://www.youtube.com/embed/RRxQQxiM7AA?feature=oembed&autoplay=1",
            "alt_text": "How to use Slack?",
            "thumbnail_url": "https://i.ytimg.com/vi/RRxQQxiM7AA/hqdefault.jpg",
        }
        VideoBlock(**input).validate_json()

    def test_required_error(self):
        # title is missing
        input = {
            "type": "video",
            "video_url": "https://www.youtube.com/embed/RRxQQxiM7AA?feature=oembed&autoplay=1",
            "alt_text": "How to use Slack?",
            "thumbnail_url": "https://i.ytimg.com/vi/RRxQQxiM7AA/hqdefault.jpg",
        }
        with self.assertRaises(SlackObjectFormationError):
            VideoBlock(**input).validate_json()

    def test_title_length_199(self):
        input = {
            "type": "video",
            "title": {
                "type": "plain_text",
                "text": "1234567890" * 19 + "123456789",
            },
            "video_url": "https://www.youtube.com/embed/RRxQQxiM7AA?feature=oembed&autoplay=1",
            "alt_text": "How to use Slack?",
            "thumbnail_url": "https://i.ytimg.com/vi/RRxQQxiM7AA/hqdefault.jpg",
        }
        VideoBlock(**input).validate_json()

    def test_title_length_200(self):
        input = {
            "type": "video",
            "title": {
                "type": "plain_text",
                "text": "1234567890" * 20,
            },
            "video_url": "https://www.youtube.com/embed/RRxQQxiM7AA?feature=oembed&autoplay=1",
            "alt_text": "How to use Slack?",
            "thumbnail_url": "https://i.ytimg.com/vi/RRxQQxiM7AA/hqdefault.jpg",
        }
        with self.assertRaises(SlackObjectFormationError):
            VideoBlock(**input).validate_json()


# ----------------------------------------------
# RichTextBlock
# ----------------------------------------------


class RichTextBlockTests(unittest.TestCase):
    def test_document(self):
        inputs = [
            {
                "type": "rich_text",
                "elements": [
                    {
                        "type": "rich_text_section",
                        "elements": [{"type": "text", "text": "Hello there, I am a basic rich text block!"}],
                    }
                ],
            },
            {
                "type": "rich_text",
                "elements": [
                    {
                        "type": "rich_text_section",
                        "elements": [
                            {"type": "text", "text": "Hello there, "},
                            {"type": "text", "text": "I am a bold rich text block!", "style": {"bold": True}},
                        ],
                    }
                ],
            },
            {
                "type": "rich_text",
                "elements": [
                    {
                        "type": "rich_text_section",
                        "elements": [
                            {"type": "text", "text": "Hello there, "},
                            {"type": "text", "text": "I am an italic rich text block!", "style": {"italic": True}},
                        ],
                    }
                ],
            },
            {
                "type": "rich_text",
                "elements": [
                    {
                        "type": "rich_text_section",
                        "elements": [
                            {"type": "text", "text": "Hello there, "},
                            {"type": "text", "text": "I am a strikethrough rich text block!", "style": {"strike": True}},
                        ],
                    }
                ],
            },
        ]
        for input in inputs:
            self.assertDictEqual(input, RichTextBlock(**input).to_dict())

    def test_complex(self):
        self.maxDiff = None
        dict_block = {
            "type": "rich_text",
            "block_id": "3Uk3Q",
            "elements": [
                {
                    "type": "rich_text_section",
                    "elements": [
                        {"type": "text", "text": "Hey!", "style": {"bold": True}},
                        {"type": "text", "text": " this is "},
                        {"type": "text", "text": "very", "style": {"strike": True}},
                        {"type": "text", "text": " rich text "},
                        {"type": "text", "text": "block", "style": {"code": True}},
                        {"type": "text", "text": " "},
                        {"type": "text", "text": "test", "style": {"italic": True}},
                        {"type": "link", "url": "https://slack.com", "text": "Slack website!"},
                    ],
                },
                {
                    "type": "rich_text_list",
                    "elements": [
                        {"type": "rich_text_section", "elements": [{"type": "text", "text": "a"}]},
                        {"type": "rich_text_section", "elements": [{"type": "text", "text": "b"}]},
                    ],
                    "style": "ordered",
                    "indent": 0,
                    "border": 0,
                },
                {
                    "type": "rich_text_list",
                    "elements": [{"type": "rich_text_section", "elements": [{"type": "text", "text": "bb"}]}],
                    "style": "ordered",
                    "indent": 1,
                    "border": 0,
                },
                {
                    "type": "rich_text_list",
                    "elements": [{"type": "rich_text_section", "elements": [{"type": "text", "text": "BBB"}]}],
                    "style": "ordered",
                    "indent": 2,
                    "border": 0,
                },
                {
                    "type": "rich_text_list",
                    "elements": [{"type": "rich_text_section", "elements": [{"type": "text", "text": "c"}]}],
                    "style": "ordered",
                    "indent": 0,
                    "offset": 2,
                    "border": 0,
                },
                {"type": "rich_text_section", "elements": [{"type": "text", "text": "\n"}]},
                {
                    "type": "rich_text_list",
                    "elements": [
                        {"type": "rich_text_section", "elements": [{"type": "text", "text": "todo"}]},
                        {"type": "rich_text_section", "elements": [{"type": "text", "text": "todo"}]},
                        {"type": "rich_text_section", "elements": [{"type": "text", "text": "todo"}]},
                    ],
                    "style": "bullet",
                    "indent": 0,
                    "border": 0,
                },
                {"type": "rich_text_section", "elements": [{"type": "text", "text": "\n"}]},
                {"type": "rich_text_quote", "elements": [{"type": "text", "text": "this is very important"}]},
                {
                    "type": "rich_text_preformatted",
                    "elements": [{"type": "text", "text": 'print("Hello world")'}],
                    "border": 0,
                },
                {
                    "type": "rich_text_section",
                    "elements": [
                        {"type": "user", "user_id": "WJC6QG0MS"},
                        {"type": "text", "text": " "},
                        {"type": "usergroup", "usergroup_id": "S01BL602YLU"},
                        {"type": "text", "text": " "},
                        {"type": "channel", "channel_id": "C02GD0YEHDJ"},
                        {
                            "type": "date",
                            "timestamp": "1628633089",
                            "format": "{date_long}",
                            "url": "https://slack.com",
                            "fallback": "August 10, 2021",
                        },
                        {"type": "date", "timestamp": "1720710212", "format": "{date_num} at {time}", "fallback": "timey"},
                        {
                            "type": "date",
                            "timestamp": "1628633089",
                            "format": "{date_short_pretty}",
                            "url": "https://slack.com",
                        },
                        {
                            "type": "date",
                            "timestamp": "1628633089",
                            "format": "{ago}",
                        },
                    ],
                },
            ],
        }
        self.assertDictEqual(dict_block, RichTextBlock(**dict_block).to_dict())
        self.assertDictEqual(dict_block, Block.parse(dict_block).to_dict())

        _ = RichTextElementParts
        class_block = RichTextBlock(
            block_id="3Uk3Q",
            elements=[
                RichTextSectionElement(
                    elements=[
                        _.Text(text="Hey!", style=_.TextStyle(bold=True)),
                        _.Text(text=" this is "),
                        _.Text(text="very", style=_.TextStyle(strike=True)),
                        _.Text(text=" rich text "),
                        _.Text(text="block", style=_.TextStyle(code=True)),
                        _.Text(text=" "),
                        _.Text(text="test", style=_.TextStyle(italic=True)),
                        _.Link(text="Slack website!", url="https://slack.com"),
                    ]
                ),
                RichTextListElement(
                    elements=[
                        RichTextSectionElement(elements=[_.Text(text="a")]),
                        RichTextSectionElement(elements=[_.Text(text="b")]),
                    ],
                    style="ordered",
                    indent=0,
                    border=0,
                ),
                RichTextListElement(
                    elements=[RichTextSectionElement(elements=[_.Text(text="bb")])],
                    style="ordered",
                    indent=1,
                    border=0,
                ),
                RichTextListElement(
                    elements=[RichTextSectionElement(elements=[_.Text(text="BBB")])],
                    style="ordered",
                    indent=2,
                    border=0,
                ),
                RichTextListElement(
                    elements=[RichTextSectionElement(elements=[_.Text(text="c")])],
                    style="ordered",
                    indent=0,
                    offset=2,
                    border=0,
                ),
                RichTextSectionElement(elements=[_.Text(text="\n")]),
                RichTextListElement(
                    elements=[
                        RichTextSectionElement(elements=[_.Text(text="todo")]),
                        RichTextSectionElement(elements=[_.Text(text="todo")]),
                        RichTextSectionElement(elements=[_.Text(text="todo")]),
                    ],
                    style="bullet",
                    indent=0,
                    border=0,
                ),
                RichTextSectionElement(elements=[_.Text(text="\n")]),
                RichTextQuoteElement(elements=[_.Text(text="this is very important")]),
                RichTextPreformattedElement(
                    elements=[_.Text(text='print("Hello world")')],
                    border=0,
                ),
                RichTextSectionElement(
                    elements=[
                        _.User(user_id="WJC6QG0MS"),
                        _.Text(text=" "),
                        _.UserGroup(usergroup_id="S01BL602YLU"),
                        _.Text(text=" "),
                        _.Channel(channel_id="C02GD0YEHDJ"),
                        _.Date(
                            timestamp="1628633089", format="{date_long}", url="https://slack.com", fallback="August 10, 2021"
                        ),
                        _.Date(timestamp="1720710212", format="{date_num} at {time}", fallback="timey"),
                        _.Date(timestamp="1628633089", format="{date_short_pretty}", url="https://slack.com"),
                        _.Date(timestamp="1628633089", format="{ago}"),
                    ]
                ),
            ],
        )
        self.assertDictEqual(dict_block, class_block.to_dict())

    def test_elements_are_parsed(self):
        dict_block = {
            "type": "rich_text",
            "elements": [
                {
                    "type": "rich_text_section",
                    "elements": [{"type": "text", "text": "Hello there, I am a basic rich text block!"}],
                },
                {
                    "type": "rich_text_quote",
                    "elements": [{"type": "text", "text": "this is very important"}],
                },
                {
                    "type": "rich_text_preformatted",
                    "elements": [{"type": "text", "text": 'print("Hello world")'}],
                },
                {
                    "type": "rich_text_list",
                    "elements": [
                        {"type": "rich_text_section", "elements": [{"type": "text", "text": "a"}]},
                    ],
                },
            ],
        }
        block = RichTextBlock(**dict_block)
        self.assertIsInstance(block.elements[0], RichTextSectionElement)
        self.assertIsInstance(block.elements[0].elements[0], RichTextElementParts.Text)
        self.assertIsInstance(block.elements[1], RichTextQuoteElement)
        self.assertIsInstance(block.elements[1].elements[0], RichTextElementParts.Text)
        self.assertIsInstance(block.elements[2], RichTextPreformattedElement)
        self.assertIsInstance(block.elements[2].elements[0], RichTextElementParts.Text)
        self.assertIsInstance(block.elements[3], RichTextListElement)
        self.assertIsInstance(block.elements[3].elements[0], RichTextSectionElement)
        self.assertIsInstance(block.elements[3].elements[0].elements[0], RichTextElementParts.Text)

    def test_parsing_empty_block_elements(self):
        empty_element_block = {
            "block_id": "my-block",
            "type": "rich_text",
            "elements": [
                {"type": "rich_text_section", "elements": []},
                {"type": "rich_text_list", "style": "bullet", "elements": []},
                {"type": "rich_text_preformatted", "elements": []},
                {"type": "rich_text_quote", "elements": []},
            ],
        }
        block = RichTextBlock(**empty_element_block)
        self.assertIsInstance(block.elements[0], RichTextSectionElement)
        self.assertIsNotNone(block.elements[0].elements)
        self.assertIsNotNone(block.elements[1].elements)
        self.assertIsNotNone(block.elements[2].elements)
        self.assertIsNotNone(block.elements[3].elements)

        block_dict = block.to_dict()
        self.assertIsNotNone(block_dict["elements"][0].get("elements"))
        self.assertIsNotNone(block_dict["elements"][1].get("elements"))
        self.assertIsNotNone(block_dict["elements"][2].get("elements"))
        self.assertIsNotNone(block_dict["elements"][3].get("elements"))
