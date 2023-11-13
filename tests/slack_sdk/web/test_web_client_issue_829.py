import unittest

import slack_sdk.errors as err
from slack_sdk.web import WebClient
from tests.slack_sdk.web.mock_web_api_server import (
    setup_mock_web_api_server,
    cleanup_mock_web_api_server,
)


class TestWebClient_Issue_829(unittest.TestCase):
    def setUp(self):
        setup_mock_web_api_server(self)

    def tearDown(self):
        cleanup_mock_web_api_server(self)

    def test_html_response_body_issue_829(self):
        client = WebClient(base_url="http://localhost:8888")
        try:
            client.users_list(token="xoxb-error_html_response")
            self.fail("SlackApiError expected here")
        except err.SlackApiError as e:
            self.assertTrue(
                str(e).startswith("The request to the Slack API failed. (url: http://"),
                e,
            )
            self.assertIsInstance(e.response.status_code, int)
            self.assertFalse(e.response["ok"])
            self.assertTrue(
                e.response["error"].startswith("Received a response in a non-JSON format: <!DOCTYPE "),
                e.response["error"],
            )
