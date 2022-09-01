import unittest
from typing import Dict, Sequence, Union

import pytest

from slack_sdk.models.attachments import Attachment
from slack_sdk.models.blocks import Block
from slack_sdk.web.internal_utils import _build_unexpected_body_error_message, _parse_web_class_objects


class TestInternalUtils(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    error_html_response_body = '<!DOCTYPE html>\n<html lang="en">\n<head>\n\t<meta charset="utf-8">\n\t<title>Server Error | Slack</title>\n\t<meta name="author" content="Slack">\n\t<style></style>\n</head>\n<body>\n\t<nav class="top persistent">\n\t\t<a href="https://status.slack.com/" class="logo" data-qa="logo"></a>\n\t</nav>\n\t<div id="page">\n\t\t<div id="page_contents">\n\t\t\t<h1>\n\t\t\t\t<svg width="30px" height="27px" viewBox="0 0 60 54" class="warning_icon"><path d="" fill="#D94827"/></svg>\n\t\t\t\tServer Error\n\t\t\t</h1>\n\t\t\t<div class="card">\n\t\t\t\t<p>It seems like there’s a problem connecting to our servers, and we’re investigating the issue.</p>\n\t\t\t\t<p>Please <a href="https://status.slack.com/">check our Status page for updates</a>.</p>\n\t\t\t</div>\n\t\t</div>\n\t</div>\n\t<script type="text/javascript">\n\t\tif (window.desktop) {\n\t\t\tdocument.documentElement.className = \'desktop\';\n\t\t}\n\n\t\tvar FIVE_MINS = 5 * 60 * 1000;\n\t\tvar TEN_MINS = 10 * 60 * 1000;\n\n\t\tfunction randomBetween(min, max) {\n\t\t\treturn Math.floor(Math.random() * (max - (min + 1))) + min;\n\t\t}\n\n\t\twindow.setTimeout(function () {\n\t\t\twindow.location.reload(true);\n\t\t}, randomBetween(FIVE_MINS, TEN_MINS));\n\t</script>\n</body>\n</html>'

    def test_build_unexpected_body_error_message(self):
        message = _build_unexpected_body_error_message(self.error_html_response_body)
        assert message.startswith(
            """Received a response in a non-JSON format: <!DOCTYPE html><html lang="en"><head><meta charset="utf-8">"""
        )


@pytest.mark.parametrize(
    "initial_blocks",
    [
        [Block(block_id="42"), Block(block_id="24")],  # list
        (
            Block(block_id="42"),
            Block(block_id="24"),
        ),  # tuple
    ],
)
def test_can_parse_sequence_of_blocks(initial_blocks: Sequence[Union[Dict, Block]]):
    kwargs = {"blocks": initial_blocks}

    _parse_web_class_objects(kwargs)

    assert kwargs["blocks"]

    for block in kwargs["blocks"]:
        assert isinstance(block, Dict)


@pytest.mark.parametrize(
    "initial_attachments",
    [
        [Attachment(text="foo"), Attachment(text="bar")],  # list
        (
            Attachment(text="foo"),
            Attachment(text="bar"),
        ),  # tuple
    ],
)
def test_can_parse_sequence_of_attachments(initial_attachments: Sequence[Union[Dict, Attachment]]):
    kwargs = {"attachments": initial_attachments}

    _parse_web_class_objects(kwargs)

    assert kwargs["attachments"]

    for attachment in kwargs["attachments"]:
        assert isinstance(attachment, Dict)
