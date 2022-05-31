import unittest
from os.path import dirname

from slack_sdk.web import WebClient
from tests.slack_sdk.web.mock_web_api_server import (
    setup_mock_web_api_server,
    cleanup_mock_web_api_server,
)


class TestWebClient_Issue_900(unittest.TestCase):
    def setUp(self):
        setup_mock_web_api_server(self)

    def tearDown(self):
        cleanup_mock_web_api_server(self)

    def test_if_it_works_with_default_params(self):
        client = WebClient(base_url="http://localhost:8888", token="xoxb-api_test", team_id="T111")
        client.files_upload(file=f"{dirname(__file__)}/test_web_client_issue_900.py")
