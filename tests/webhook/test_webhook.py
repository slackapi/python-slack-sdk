import unittest
import socket
import urllib

from slack.web.classes.attachments import Attachment, AttachmentField
from slack.web.classes.blocks import SectionBlock, ImageBlock
from slack.webhook import WebhookClient, WebhookResponse
from tests.webhook.mock_web_api_server import (
    cleanup_mock_web_api_server,
    setup_mock_web_api_server,
)


class TestWebhook(unittest.TestCase):
    def setUp(self):
        setup_mock_web_api_server(self)

    def tearDown(self):
        cleanup_mock_web_api_server(self)

    def test_send(self):
        client = WebhookClient("http://localhost:8888")

        resp: WebhookResponse = client.send(text="hello!")
        self.assertEqual(200, resp.status_code)
        self.assertEqual("ok", resp.body)

        resp = client.send(text="hello!", response_type="in_channel")
        self.assertEqual("ok", resp.body)

    def test_send_with_url_unfurl_opts_issue_1045(self):
        client = WebhookClient("http://localhost:8888")
        resp: WebhookResponse = client.send(
            text="<https://imgs.xkcd.com/comics/1991_and_2021_2x.png|XKCD>",
            unfurl_links=False,
            unfurl_media=False,
        )
        self.assertEqual(200, resp.status_code)
        self.assertEqual("ok", resp.body)

    def test_send_blocks(self):
        client = WebhookClient("http://localhost:8888")

        resp = client.send(
            text="hello!",
            response_type="ephemeral",
            blocks=[
                SectionBlock(text="Some text"),
                ImageBlock(image_url="image.jpg", alt_text="an image"),
            ],
        )
        self.assertEqual("ok", resp.body)

        resp = client.send(
            text="hello!",
            response_type="ephemeral",
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "This is a mrkdwn section block :ghost: *this is bold*, and ~this is crossed out~, and <https://google.com|this is a link>",
                    },
                },
                {"type": "divider"},
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": "Pick a date for the deadline."},
                    "accessory": {
                        "type": "datepicker",
                        "initial_date": "1990-04-28",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Select a date",
                        },
                    },
                },
            ],
        )
        self.assertEqual("ok", resp.body)

        resp = client.send(
            text="hello!",
            response_type="ephemeral",
            blocks=[
                SectionBlock(text="Some text"),
                ImageBlock(image_url="image.jpg", alt_text="an image"),
            ],
        )
        self.assertEqual("ok", resp.body)

    def test_send_attachments(self):
        client = WebhookClient("http://localhost:8888")

        resp = client.send(
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
                                "text": "This is a mrkdwn section block :ghost: *this is bold*, and ~this is crossed out~, and <https://google.com|this is a link>",
                            },
                        },
                        {"type": "divider"},
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": "Pick a date for the deadline.",
                            },
                            "accessory": {
                                "type": "datepicker",
                                "initial_date": "1990-04-28",
                                "placeholder": {
                                    "type": "plain_text",
                                    "text": "Select a date",
                                },
                            },
                        },
                    ],
                }
            ],
        )
        self.assertEqual("ok", resp.body)

        resp = client.send(
            text="hello!",
            response_type="ephemeral",
            attachments=[
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
                )
            ],
        )
        self.assertEqual("ok", resp.body)

    def test_send_dict(self):
        client = WebhookClient("http://localhost:8888")
        resp: WebhookResponse = client.send_dict({"text": "hello!"})
        self.assertEqual(200, resp.status_code)
        self.assertEqual("ok", resp.body)

    def test_timeout_issue_712(self):
        client = WebhookClient(url="http://localhost:8888/timeout", timeout=1)
        with self.assertRaises(socket.timeout):
            client.send_dict({"text": "hello!"})

    def test_error_response(self):
        client = WebhookClient(url="http://localhost:8888/error")
        resp: WebhookResponse = client.send_dict({"text": "hello!"})
        self.assertEqual(500, resp.status_code)
        self.assertTrue(resp.body.startswith("<!DOCTYPE html>"))

    def test_proxy_issue_714(self):
        client = WebhookClient(url="http://localhost:8888", proxy="http://invalid-host:9999")
        with self.assertRaises(urllib.error.URLError):
            client.send_dict({"text": "hello!"})

    def test_user_agent_customization_issue_769(self):
        client = WebhookClient(
            url="http://localhost:8888/user-agent-this_is-test",
            user_agent_prefix="this_is",
            user_agent_suffix="test",
        )
        resp = client.send_dict({"text": "hi!"})
        self.assertEqual(resp.body, "ok")
