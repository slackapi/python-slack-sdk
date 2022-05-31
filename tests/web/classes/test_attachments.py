import unittest

from slack.errors import SlackObjectFormationError
from slack.web.classes.actions import ActionButton, ActionLinkButton
from slack.web.classes.blocks import SectionBlock, ImageBlock
from slack.web.classes.attachments import (
    Attachment,
    BlockAttachment,
    AttachmentField,
    InteractiveAttachment,
)
from tests.web.classes import STRING_301_CHARS


class FieldTests(unittest.TestCase):
    def test_basic_json(self):
        self.assertDictEqual(
            AttachmentField(title="field", value="something", short=False).to_dict(),
            {"title": "field", "value": "something", "short": False},
        )


class AttachmentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.simple = Attachment(text="some_text")

    def test_basic_json(self):
        self.assertDictEqual(Attachment(text="some text").to_dict(), {"text": "some text", "fields": []})

        self.assertDictEqual(
            Attachment(
                text="attachment text",
                title="Attachment",
                fallback="fallback_text",
                pretext="some_pretext",
                title_link="link in title",
                fields=[AttachmentField(title=f"field_{i}_title", value=f"field_{i}_value") for i in range(5)],
                color="#FFFF00",
                author_name="John Doe",
                author_link="http://johndoeisthebest.com",
                author_icon="http://johndoeisthebest.com/avatar.jpg",
                thumb_url="thumbnail URL",
                footer="and a footer",
                footer_icon="link to footer icon",
                ts=123456789,
                markdown_in=["fields"],
            ).to_dict(),
            {
                "text": "attachment text",
                "author_name": "John Doe",
                "author_link": "http://johndoeisthebest.com",
                "author_icon": "http://johndoeisthebest.com/avatar.jpg",
                "footer": "and a footer",
                "title": "Attachment",
                "footer_icon": "link to footer icon",
                "pretext": "some_pretext",
                "ts": 123456789,
                "fallback": "fallback_text",
                "title_link": "link in title",
                "color": "#FFFF00",
                "thumb_url": "thumbnail URL",
                "fields": [
                    {"title": "field_0_title", "value": "field_0_value", "short": True},
                    {"title": "field_1_title", "value": "field_1_value", "short": True},
                    {"title": "field_2_title", "value": "field_2_value", "short": True},
                    {"title": "field_3_title", "value": "field_3_value", "short": True},
                    {"title": "field_4_title", "value": "field_4_value", "short": True},
                ],
                "mrkdwn_in": ["fields"],
            },
        )

    def test_footer_length(self):
        with self.assertRaises(SlackObjectFormationError):
            self.simple.footer = STRING_301_CHARS
            self.simple.to_dict()

    def test_ts_without_footer(self):
        with self.assertRaises(SlackObjectFormationError):
            self.simple.ts = 123456789
            self.simple.to_dict()

    def test_markdown_in_invalid(self):
        with self.assertRaises(SlackObjectFormationError):
            self.simple.markdown_in = ["nothing"]
            self.simple.to_dict()

    def test_color_valid(self):
        with self.assertRaises(SlackObjectFormationError):
            self.simple.color = "red"
            self.simple.to_dict()

        with self.assertRaises(SlackObjectFormationError):
            self.simple.color = "#ZZZZZZ"
            self.simple.to_dict()

        self.simple.color = "#bada55"
        self.assertEqual(self.simple.to_dict()["color"], "#bada55")

        self.simple.color = "good"
        self.assertEqual(self.simple.to_dict()["color"], "good")

    def test_image_url_and_thumb_url(self):
        with self.assertRaises(SlackObjectFormationError):
            self.simple.thumb_url = "some URL"
            self.simple.image_url = "some URL"
            self.simple.to_dict()

        self.simple.image_url = None
        self.simple.to_dict()

    def author_name_without_author_link(self):
        with self.assertRaises(SlackObjectFormationError):
            self.simple.author_name = "http://google.com"
            self.simple.to_dict()

        self.simple.author_name = None
        self.simple.to_dict()

    def author_icon_without_author_name(self):
        with self.assertRaises(SlackObjectFormationError):
            self.simple.author_icon = "http://google.com/images.jpg"
            self.simple.to_dict()

        self.simple.author_icon = None
        self.simple.to_dict()


class InteractiveAttachmentTests(unittest.TestCase):
    def test_basic_json(self):
        actions = [
            ActionButton(name="button_1", text="Click me", value="button_value_1"),
            ActionLinkButton(text="navigate", url="http://google.com"),
        ]
        self.assertDictEqual(
            InteractiveAttachment(text="some text", callback_id="abc123", actions=actions).to_dict(),
            {
                "text": "some text",
                "fields": [],
                "callback_id": "abc123",
                "actions": [a.to_dict() for a in actions],
            },
        )

        self.assertDictEqual(
            InteractiveAttachment(
                actions=actions,
                callback_id="cb_123",
                text="attachment text",
                title="Attachment",
                fallback="fallback_text",
                pretext="some_pretext",
                title_link="link in title",
                fields=[AttachmentField(title=f"field_{i}_title", value=f"field_{i}_value") for i in range(5)],
                color="#FFFF00",
                author_name="John Doe",
                author_link="http://johndoeisthebest.com",
                author_icon="http://johndoeisthebest.com/avatar.jpg",
                thumb_url="thumbnail URL",
                footer="and a footer",
                footer_icon="link to footer icon",
                ts=123456789,
                markdown_in=["fields"],
            ).to_dict(),
            {
                "text": "attachment text",
                "callback_id": "cb_123",
                "actions": [a.to_dict() for a in actions],
                "author_name": "John Doe",
                "author_link": "http://johndoeisthebest.com",
                "author_icon": "http://johndoeisthebest.com/avatar.jpg",
                "footer": "and a footer",
                "title": "Attachment",
                "footer_icon": "link to footer icon",
                "pretext": "some_pretext",
                "ts": 123456789,
                "fallback": "fallback_text",
                "title_link": "link in title",
                "color": "#FFFF00",
                "thumb_url": "thumbnail URL",
                "fields": [
                    {"title": "field_0_title", "value": "field_0_value", "short": True},
                    {"title": "field_1_title", "value": "field_1_value", "short": True},
                    {"title": "field_2_title", "value": "field_2_value", "short": True},
                    {"title": "field_3_title", "value": "field_3_value", "short": True},
                    {"title": "field_4_title", "value": "field_4_value", "short": True},
                ],
                "mrkdwn_in": ["fields"],
            },
        )

    def test_actions_length(self):
        actions = [ActionButton(name="button_1", text="Click me", value="button_value_1")] * 6

        with self.assertRaises(SlackObjectFormationError):
            InteractiveAttachment(text="some text", callback_id="abc123", actions=actions).to_dict(),


class BlockAttachmentTests(unittest.TestCase):
    def test_basic_json(self):
        blocks = [
            SectionBlock(text="Some text"),
            ImageBlock(image_url="image.jpg", alt_text="an image"),
        ]

        self.assertDictEqual(
            BlockAttachment(fallback="foo", blocks=blocks).to_dict(),
            {"fallback": "foo", "blocks": [b.to_dict() for b in blocks]},
        )
