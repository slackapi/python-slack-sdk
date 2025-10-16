import unittest
from typing import List

from slack.errors import SlackObjectFormationError
from slack.web.classes.blocks import (
    ActionsBlock,
    ContextBlock,
    DividerBlock,
    HeaderBlock,
    ImageBlock,
    SectionBlock,
    InputBlock,
    FileBlock,
    Block,
    CallBlock,
)
from slack.web.classes.elements import ButtonElement, ImageElement, LinkButtonElement
from slack.web.classes.objects import PlainTextObject, MarkdownTextObject
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
        self.assertDictEqual(input, Block.parse(input).to_dict())

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

        button = LinkButtonElement(text="Click me!", url="http://google.com")
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
        self.assertDictEqual(input, Block.parse(input).to_dict())

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
        self.assertDictEqual(input, Block.parse(input).to_dict())

    def test_json(self):
        self.assertDictEqual(
            {
                "image_url": "http://google.com",
                "alt_text": "not really an image",
                "type": "image",
            },
            ImageBlock(image_url="http://google.com", alt_text="not really an image").to_dict(),
        )

    def test_image_url_length(self):
        with self.assertRaises(SlackObjectFormationError):
            ImageBlock(image_url=STRING_3001_CHARS, alt_text="text").to_dict()

    def test_alt_text_length(self):
        with self.assertRaises(SlackObjectFormationError):
            ImageBlock(image_url="http://google.com", alt_text=STRING_3001_CHARS).to_dict()

    def test_title_length(self):
        with self.assertRaises(SlackObjectFormationError):
            ImageBlock(image_url="http://google.com", alt_text="text", title=STRING_3001_CHARS).to_dict()


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
        self.assertDictEqual(input, Block.parse(input).to_dict())

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
            LinkButtonElement(text="URL Button", url="http://google.com"),
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
        self.assertDictEqual(input, Block.parse(input).to_dict())

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
            self.assertDictEqual(input, Block.parse(input).to_dict())


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
        self.assertDictEqual(input, Block.parse(input).to_dict())


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
