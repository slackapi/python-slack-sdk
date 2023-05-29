import unittest

import slack_sdk.errors as err
from slack_sdk.web.async_client import AsyncWebClient
from tests.helpers import async_test
from tests.slack_sdk.web.mock_web_api_server import (
    setup_mock_web_api_server,
    cleanup_mock_web_api_server,
)


class TestWebClient_Issue_829(unittest.TestCase):
    def setUp(self):
        setup_mock_web_api_server(self)

    def tearDown(self):
        cleanup_mock_web_api_server(self)

    @async_test
    async def test_html_response_body_issue_829_async(self):
        client = AsyncWebClient(base_url="http://localhost:8888")
        try:
            await client.users_list(token="xoxb-error_html_response")
            self.fail("SlackApiError expected here")
        except err.SlackApiError as e:
            self.assertEqual(
                "The request to the Slack API failed. (url: http://localhost:8888/users.list, status: 503)\n"
                "The server responded with: {}",
                str(e),
            )
