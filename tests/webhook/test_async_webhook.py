import asyncio
import unittest

import aiohttp

from slack.web.classes.attachments import Attachment, AttachmentField
from slack.web.classes.blocks import SectionBlock, ImageBlock
from slack.webhook import AsyncWebhookClient, WebhookResponse
from tests.helpers import async_test
from tests.webhook.mock_web_api_server import cleanup_mock_web_api_server, setup_mock_web_api_server


class TestAsyncWebhook(unittest.TestCase):

    def setUp(self):
        setup_mock_web_api_server(self)

    def tearDown(self):
        cleanup_mock_web_api_server(self)

    @async_test
    async def test_send(self):
        client = AsyncWebhookClient("http://localhost:8888")

        resp: WebhookResponse = await client.send(text="hello!")
        self.assertEqual(200, resp.status_code)
        self.assertEqual("ok", resp.body)

        resp = await client.send(text="hello!", response_type="in_channel")
        self.assertEqual("ok", resp.body)

    @async_test
    async def test_send_blocks(self):
        client = AsyncWebhookClient("http://localhost:8888")

        resp = await client.send(
            text="hello!",
            response_type="ephemeral",
            blocks=[
                SectionBlock(text="Some text"),
                ImageBlock(image_url="image.jpg", alt_text="an image")
            ]
        )
        self.assertEqual("ok", resp.body)

        resp = await client.send(
            text="hello!",
            response_type="ephemeral",
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "This is a mrkdwn section block :ghost: *this is bold*, and ~this is crossed out~, and <https://google.com|this is a link>"
                    }
                },
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "Pick a date for the deadline."
                    },
                    "accessory": {
                        "type": "datepicker",
                        "initial_date": "1990-04-28",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Select a date",
                        }
                    }
                }
            ]
        )
        self.assertEqual("ok", resp.body)

        resp = await client.send(
            text="hello!",
            response_type="ephemeral",
            blocks=[
                SectionBlock(text="Some text"),
                ImageBlock(image_url="image.jpg", alt_text="an image")
            ]
        )
        self.assertEqual("ok", resp.body)

    @async_test
    async def test_send_attachments(self):
        client = AsyncWebhookClient("http://localhost:8888")

        resp = await client.send(
            text="hello!",
            response_type="ephemeral",
            attachments=[
                {
                    "color": "#f2c744",
                    "blocks": [
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": "This is a mrkdwn section block :ghost: *this is bold*, and ~this is crossed out~, and <https://google.com|this is a link>"
                            }
                        },
                        {
                            "type": "divider"
                        },
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": "Pick a date for the deadline."
                            },
                            "accessory": {
                                "type": "datepicker",
                                "initial_date": "1990-04-28",
                                "placeholder": {
                                    "type": "plain_text",
                                    "text": "Select a date",
                                }
                            }
                        }
                    ]
                }
            ]
        )
        self.assertEqual("ok", resp.body)

        resp = await client.send(
            text="hello!",
            response_type="ephemeral",
            attachments=[
                Attachment(
                    text="attachment text",
                    title="Attachment",
                    fallback="fallback_text",
                    pretext="some_pretext",
                    title_link="link in title",
                    fields=[
                        AttachmentField(title=f"field_{i}_title", value=f"field_{i}_value")
                        for i in range(5)
                    ],
                    color="#FFFF00",
                    author_name="John Doe",
                    author_link="http://johndoeisthebest.com",
                    author_icon="http://johndoeisthebest.com/avatar.jpg",
                    thumb_url="thumbnail URL",
                    footer="and a footer",
                    footer_icon="link to footer icon",
                    ts=123456789,
                    markdown_in=["fields"],
                )
            ]
        )
        self.assertEqual("ok", resp.body)

    @async_test
    async def test_send_dict(self):
        client = AsyncWebhookClient("http://localhost:8888")
        resp: WebhookResponse = await client.send_dict({"text": "hello!"})
        self.assertEqual(200, resp.status_code)
        self.assertEqual("ok", resp.body)

    @async_test
    async def test_timeout_issue_712(self):
        client = AsyncWebhookClient(url="http://localhost:8888/timeout", timeout=1)
        with self.assertRaises(Exception):
            await client.send_dict({"text": "hello!"})

    @async_test
    async def test_proxy_issue_714(self):
        client = AsyncWebhookClient(url="http://localhost:8888", proxy="http://invalid-host:9999")
        with self.assertRaises(Exception):
            await client.send_dict({"text": "hello!"})

    @async_test
    async def test_user_agent_customization_issue_769(self):
        client = AsyncWebhookClient(
            url="http://localhost:8888/user-agent-this_is-test",
            user_agent_prefix="this_is",
            user_agent_suffix="test",
        )
        resp = await client.send_dict({"text": "hi!"})
        self.assertEqual(resp.body, "ok")
