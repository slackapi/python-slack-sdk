import json
import unittest
from io import BytesIO
from typing import Dict, Sequence, Union

import pytest

from slack_sdk.models.attachments import Attachment
from slack_sdk.models.blocks import Block, DividerBlock
from slack_sdk.web.internal_utils import (
    _build_unexpected_body_error_message,
    _parse_web_class_objects,
    _to_v2_file_upload_item,
    _next_cursor_is_present,
)


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

    def test_can_parse_sequence_of_blocks(self):
        for blocks in [
            [Block(block_id="42"), Block(block_id="24")],  # list
            (Block(block_id="42"), Block(block_id="24")),  # tuple
        ]:
            kwargs = {"blocks": blocks}
            _parse_web_class_objects(kwargs)
            assert kwargs["blocks"]
            for block in kwargs["blocks"]:
                assert isinstance(block, Dict)

    def test_can_parse_sequence_of_attachments(self):
        for attachments in [
            [Attachment(text="foo"), Attachment(text="bar")],  # list
            (
                Attachment(text="foo"),
                Attachment(text="bar"),
            ),  # tuple
        ]:
            kwargs = {"attachments": attachments}
            _parse_web_class_objects(kwargs)
            assert kwargs["attachments"]
            for attachment in kwargs["attachments"]:
                assert isinstance(attachment, Dict)

    def test_can_parse_str_blocks(self):
        input = json.dumps([Block(block_id="42").to_dict(), Block(block_id="24").to_dict()])
        kwargs = {"blocks": input}
        _parse_web_class_objects(kwargs)
        assert isinstance(kwargs["blocks"], str)
        assert input == kwargs["blocks"]

    def test_can_parse_str_attachments(self):
        input = json.dumps([Attachment(text="foo").to_dict(), Attachment(text="bar").to_dict()])
        kwargs = {"attachments": input}
        _parse_web_class_objects(kwargs)
        assert isinstance(kwargs["attachments"], str)
        assert input == kwargs["attachments"]

    def test_can_parse_user_auth_blocks(self):
        kwargs = {
            "channel": "C12345",
            "ts": "1111.2222",
            "unfurls": {},
            "user_auth_blocks": [DividerBlock(), DividerBlock()],
        }
        _parse_web_class_objects(kwargs)
        assert isinstance(kwargs["user_auth_blocks"][0], dict)

    def test_files_upload_v2_issue_1356(self):
        content_item = _to_v2_file_upload_item({"content": "test"})
        assert content_item.get("filename") == "Uploaded file"

        filepath_item = _to_v2_file_upload_item({"file": "tests/slack_sdk/web/test_internal_utils.py"})
        assert filepath_item.get("filename") == "test_internal_utils.py"
        filepath_item = _to_v2_file_upload_item({"file": "tests/slack_sdk/web/test_internal_utils.py", "filename": "foo.py"})
        assert filepath_item.get("filename") == "foo.py"

        file_bytes = "This is a test!".encode("utf-8")
        file_bytes_item = _to_v2_file_upload_item({"file": file_bytes})
        assert file_bytes_item.get("filename") == "Uploaded file"
        file_bytes_item = _to_v2_file_upload_item({"file": file_bytes, "filename": "foo.txt"})
        assert file_bytes_item.get("filename") == "foo.txt"

        file_io = BytesIO(file_bytes)
        file_io_item = _to_v2_file_upload_item({"file": file_io})
        assert file_io_item.get("filename") == "Uploaded file"
        file_io_item = _to_v2_file_upload_item({"file": file_io, "filename": "foo.txt"})
        assert file_io_item.get("filename") == "foo.txt"

    def test_next_cursor_is_present(self):
        assert _next_cursor_is_present({"next_cursor": "next-page"}) is True
        assert _next_cursor_is_present({"next_cursor": ""}) is False
        assert _next_cursor_is_present({"next_cursor": None}) is False
        assert _next_cursor_is_present({"response_metadata": {"next_cursor": "next-page"}}) is True
        assert _next_cursor_is_present({"response_metadata": {"next_cursor": ""}}) is False
        assert _next_cursor_is_present({"response_metadata": {"next_cursor": None}}) is False
        assert _next_cursor_is_present({"something_else": {"next_cursor": "next-page"}}) is False
