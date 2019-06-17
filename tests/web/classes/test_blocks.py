import unittest

from slack.errors import SlackObjectFormationError
from slack.web.classes.blocks import (
    ActionsBlock,
    ContextBlock,
    DividerBlock,
    ImageBlock,
    SectionBlock,
)
from slack.web.classes.elements import ButtonElement, ImageElement, LinkButtonElement
from slack.web.classes.objects import PlainTextObject
from . import STRING_3001_CHARS


class DividerBlockTests(unittest.TestCase):
    def test_json(self):
        self.assertDictEqual(DividerBlock().get_json(), {"type": "divider"})


class SectionBlockTests(unittest.TestCase):
    def test_json(self):
        self.assertDictEqual(
            SectionBlock(text="some text", block_id="a_block").get_json(),
            {
                "text": {"text": "some text", "type": "mrkdwn", "verbatim": False},
                "block_id": "a_block",
                "type": "section",
            },
        )

        self.assertDictEqual(
            SectionBlock(
                text="some text", fields=[f"field{i}" for i in range(5)]
            ).get_json(),
            {
                "text": {"text": "some text", "type": "mrkdwn", "verbatim": False},
                "fields": [
                    {"text": "field0", "type": "mrkdwn", "verbatim": False},
                    {"text": "field1", "type": "mrkdwn", "verbatim": False},
                    {"text": "field2", "type": "mrkdwn", "verbatim": False},
                    {"text": "field3", "type": "mrkdwn", "verbatim": False},
                    {"text": "field4", "type": "mrkdwn", "verbatim": False},
                ],
                "type": "section",
            },
        )

        button = LinkButtonElement(text="Click me!", url="http://google.com")
        self.assertDictEqual(
            SectionBlock(text="some text", accessory=button).get_json(),
            {
                "text": {"text": "some text", "type": "mrkdwn", "verbatim": False},
                "accessory": button.get_json(),
                "type": "section",
            },
        )

    def test_text_or_fields_populated(self):
        with self.assertRaises(SlackObjectFormationError):
            SectionBlock().get_json()

    def test_fields_length(self):
        with self.assertRaises(SlackObjectFormationError):
            SectionBlock(fields=[f"field{i}" for i in range(11)]).get_json()


class ImageBlockTests(unittest.TestCase):
    def test_json(self):
        self.assertDictEqual(
            ImageBlock(
                image_url="http://google.com", alt_text="not really an image"
            ).get_json(),
            {
                "image_url": "http://google.com",
                "alt_text": "not really an image",
                "type": "image",
            },
        )

    def test_image_url_length(self):
        with self.assertRaises(SlackObjectFormationError):
            ImageBlock(image_url=STRING_3001_CHARS, alt_text="text").get_json()

    def test_alt_text_length(self):
        with self.assertRaises(SlackObjectFormationError):
            ImageBlock(
                image_url="http://google.com", alt_text=STRING_3001_CHARS
            ).get_json()

    def test_title_length(self):
        with self.assertRaises(SlackObjectFormationError):
            ImageBlock(
                image_url="http://google.com", alt_text="text", title=STRING_3001_CHARS
            ).get_json()


class ActionsBlockTests(unittest.TestCase):
    def setUp(self) -> None:
        self.elements = [
            ButtonElement(text="Click me", action_id="reg_button", value="1"),
            LinkButtonElement(text="URL Button", url="http://google.com"),
        ]

    def test_json(self):
        self.assertDictEqual(
            ActionsBlock(elements=self.elements).get_json(),
            {"elements": [e.get_json() for e in self.elements], "type": "actions"},
        )

    def test_elements_length(self):
        with self.assertRaises(SlackObjectFormationError):
            ActionsBlock(elements=self.elements * 3).get_json()


class ContextBlockTests(unittest.TestCase):
    def setUp(self) -> None:
        self.elements = [
            ImageElement(image_url="http://google.com", alt_text="google"),
            PlainTextObject(text="Just text"),
        ]

    def test_basic_json(self):
        d = ContextBlock(elements=self.elements).get_json()
        e = {
            "elements": [
                {
                    "type": "image",
                    "image_url": "http://google.com",
                    "alt_text": "google",
                },
                {"type": "plain_text", "emoji": True, "text": "Just text"},
            ],
            "type": "context",
        }

        self.assertDictEqual(d, e)

    def test_elements_length(self):
        with self.assertRaises(SlackObjectFormationError):
            ContextBlock(elements=self.elements * 6).get_json()
