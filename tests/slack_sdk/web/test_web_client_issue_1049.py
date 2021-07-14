import json
import unittest

from slack_sdk.web import WebClient
from tests.slack_sdk.web.mock_web_api_server import (
    setup_mock_web_api_server,
    cleanup_mock_web_api_server,
)


class TestWebClient_Issue_1049(unittest.TestCase):
    def setUp(self):
        setup_mock_web_api_server(self)

    def tearDown(self):
        cleanup_mock_web_api_server(self)

    def test_the_pattern(self):
        client = WebClient(
            base_url="http://localhost:8888",
            token="xoxb-admin_convo_pagination",
        )
        pages = []
        for page in client.admin_conversations_search(query="announcement"):
            pages.append(page)
        self.assertEqual(len(pages), 2)
