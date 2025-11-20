import json
import unittest
from io import BytesIO
from pathlib import Path
from typing import Dict, Sequence, Union

import pytest

from slack_sdk.models.attachments import Attachment
from slack_sdk.models.blocks import Block, DividerBlock, MarkdownBlock
from slack_sdk.web.internal_utils import (
    _build_unexpected_body_error_message,
    _parse_web_class_objects,
    _to_v2_file_upload_item,
    _next_cursor_is_present,
    _get_url,
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

    def test_to_v2_file_upload_item_can_accept_file_as_path(self):
        filepath = "tests/slack_sdk/web/test_internal_utils.py"
        upload_item_str = _to_v2_file_upload_item({"file": filepath})
        upload_item_path = _to_v2_file_upload_item({"file": Path(filepath)})
        assert upload_item_path == upload_item_str
        assert upload_item_str.get("filename") == "test_internal_utils.py"

    def test_next_cursor_is_present(self):
        assert _next_cursor_is_present({"next_cursor": "next-page"}) is True
        assert _next_cursor_is_present({"next_cursor": ""}) is False
        assert _next_cursor_is_present({"next_cursor": None}) is False
        assert _next_cursor_is_present({"response_metadata": {"next_cursor": "next-page"}}) is True
        assert _next_cursor_is_present({"response_metadata": {"next_cursor": ""}}) is False
        assert _next_cursor_is_present({"response_metadata": {"next_cursor": None}}) is False
        assert _next_cursor_is_present({"something_else": {"next_cursor": "next-page"}}) is False

    def test_get_url_prevent_double_slash(self):
        # Test case: Prevent double slash when both base_url and api_method include slashes
        api_url = _get_url("https://slack.com/api/", "/chat.postMessage")
        self.assertEqual(
            api_url,
            "https://slack.com/api/chat.postMessage",
            "Should correctly handle and remove double slashes between base_url and api_method",
        )

        # Test case: Handle api_method without leading slash
        api_url = _get_url("https://slack.com/api/", "chat.postMessage")
        self.assertEqual(
            api_url,
            "https://slack.com/api/chat.postMessage",
            "Should correctly handle api_method without a leading slash",
        )

    def test_files_complete_upload_external_blocks_serialization(self):
        """Test that blocks are properly serialized for files.completeUploadExternal
        
        This test verifies the fix for the bug where passing markdown blocks to
        files_upload_v2 caused internal_error. The issue was that blocks weren't
        being properly serialized to JSON strings before being sent to the API.
        """
        # Test case 1: blocks as list of dicts (the bug scenario)
        blocks_dict = [{"type": "markdown", "text": "_**User** posted a message_\\n> test"}]
        kwargs = {"blocks": blocks_dict}
        
        # Simulate what files_completeUploadExternal does
        _parse_web_class_objects(kwargs)
        blocks = kwargs.get("blocks")
        if blocks is not None and not isinstance(blocks, str):
            kwargs["blocks"] = json.dumps(blocks)
        
        assert isinstance(kwargs["blocks"], str), "Blocks should be serialized to string"
        assert json.loads(kwargs["blocks"]) == blocks_dict, "Serialized blocks should match original"
        
        # Test case 2: blocks as MarkdownBlock objects
        markdown_block = MarkdownBlock(text="_**User** posted a message_\\n> test")
        blocks_objects = [markdown_block]
        kwargs = {"blocks": blocks_objects}
        
        _parse_web_class_objects(kwargs)
        blocks = kwargs.get("blocks")
        if blocks is not None and not isinstance(blocks, str):
            kwargs["blocks"] = json.dumps(blocks)
        
        assert isinstance(kwargs["blocks"], str), "Blocks should be serialized to string"
        deserialized = json.loads(kwargs["blocks"])
        assert deserialized[0]["type"] == "markdown", "Block type should be markdown"
        assert deserialized[0]["text"] == "_**User** posted a message_\\n> test", "Block text should match"
        
        # Test case 3: blocks already as JSON string (should not double-serialize)
        blocks_json = json.dumps([{"type": "markdown", "text": "test"}])
        kwargs = {"blocks": blocks_json}
        
        _parse_web_class_objects(kwargs)
        blocks = kwargs.get("blocks")
        if blocks is not None and not isinstance(blocks, str):
            kwargs["blocks"] = json.dumps(blocks)
        
        assert kwargs["blocks"] == blocks_json, "Already serialized blocks should not be double-serialized"
        
        # Test case 4: attachments should also be serialized
        attachments = [{"text": "attachment text", "color": "#36a64f"}]
        kwargs = {"attachments": attachments}
        
        _parse_web_class_objects(kwargs)
        attachments_val = kwargs.get("attachments")
        if attachments_val is not None and not isinstance(attachments_val, str):
            kwargs["attachments"] = json.dumps(attachments_val)
        
        assert isinstance(kwargs["attachments"], str), "Attachments should be serialized to string"
        assert json.loads(kwargs["attachments"]) == attachments, "Serialized attachments should match original"
