import json
import unittest

from slack_sdk.web import WebClient
from tests.slack_sdk.web.mock_web_api_server import (
    setup_mock_web_api_server,
    cleanup_mock_web_api_server,
)


class TestWebClient_Issue_971(unittest.TestCase):
    def setUp(self):
        setup_mock_web_api_server(self)

    def tearDown(self):
        cleanup_mock_web_api_server(self)

    def test_text_arg_only(self):
        client = WebClient(base_url="http://localhost:8888", token="xoxb-api_test", team_id="T111")
        resp = client.chat_postMessage(channel="C111", text="test")
        self.assertTrue(resp["ok"])

    def test_blocks_with_text_arg(self):
        client = WebClient(base_url="http://localhost:8888", token="xoxb-api_test", team_id="T111")
        resp = client.chat_postMessage(channel="C111", text="test", blocks=[])
        self.assertTrue(resp["ok"])

    def test_blocks_without_text_arg(self):
        client = WebClient(base_url="http://localhost:8888", token="xoxb-api_test", team_id="T111")
        # this generates a warning because "text" is missing
        with self.assertWarns(UserWarning):
            resp = client.chat_postMessage(channel="C111", blocks=[])
        self.assertTrue(resp["ok"])

    def test_attachments_with_fallback(self):
        client = WebClient(base_url="http://localhost:8888", token="xoxb-api_test", team_id="T111")
        # this generates a warning because "text" is missing
        resp = client.chat_postMessage(channel="C111", attachments=[{"fallback": "test"}])
        self.assertTrue(resp["ok"])

    def test_attachments_with_empty_fallback(self):
        client = WebClient(base_url="http://localhost:8888", token="xoxb-api_test", team_id="T111")
        # this generates two warnings: "text" is missing, and also one attachment with no fallback
        with self.assertWarns(UserWarning):
            resp = client.chat_postMessage(channel="C111", attachments=[{"fallback": ""}])
        self.assertTrue(resp["ok"])

    def test_attachments_without_fallback(self):
        client = WebClient(base_url="http://localhost:8888", token="xoxb-api_test", team_id="T111")
        # this generates two warnings: "text" is missing, and also one attachment with no fallback
        with self.assertWarns(UserWarning):
            resp = client.chat_postMessage(channel="C111", attachments=[{}])
        self.assertTrue(resp["ok"])

    def test_multiple_attachments_one_without_fallback(self):
        client = WebClient(base_url="http://localhost:8888", token="xoxb-api_test", team_id="T111")
        # this generates two warnings: "text" is missing, and also one attachment with no fallback
        with self.assertWarns(UserWarning):
            resp = client.chat_postMessage(channel="C111", attachments=[{"fallback": "test"}, {}])
        self.assertTrue(resp["ok"])

    def test_blocks_as_deserialzed_json_without_text_arg(self):
        client = WebClient(base_url="http://localhost:8888", token="xoxb-api_test", team_id="T111")
        # this generates a warning because "text" is missing
        with self.assertWarns(UserWarning):
            resp = client.chat_postMessage(channel="C111", attachments=json.dumps([]))
        self.assertTrue(resp["ok"])

    def test_blocks_as_deserialized_json_with_text_arg(self):
        client = WebClient(base_url="http://localhost:8888", token="xoxb-api_test", team_id="T111")
        # this DOESN'T warn because the "text" arg is present
        resp = client.chat_postMessage(channel="C111", text="test", blocks=json.dumps([]))
        self.assertTrue(resp["ok"])

    def test_attachments_as_deserialzed_json_without_text_arg(self):
        client = WebClient(base_url="http://localhost:8888", token="xoxb-api_test", team_id="T111")
        # this still generates a warning because "text" is missing. The attachment has already
        # been deserialized, which isn't explicitly prohibited in the docs (but isn't recommended)
        with self.assertWarns(UserWarning):
            resp = client.chat_postMessage(channel="C111", attachments=json.dumps([{"fallback": "test"}]))
        self.assertTrue(resp["ok"])

    def test_attachments_as_deserialized_json_with_text_arg(self):
        client = WebClient(base_url="http://localhost:8888", token="xoxb-api_test", team_id="T111")
        # this DOESN'T warn because the text arg is present (attachment already deserialized)
        resp = client.chat_postMessage(channel="C111", text="test", attachments=json.dumps([]))
        self.assertTrue(resp["ok"])
