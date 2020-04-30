import asyncio
import re
import unittest

import slack
import slack.errors as err
from slack.web.urllib_client import UrllibWebClient
from tests.helpers import async_test
from tests.web.mock_web_api_server import setup_mock_web_api_server, cleanup_mock_web_api_server


class TestWebClient(unittest.TestCase):

    def setUp(self):
        setup_mock_web_api_server(self)
        self.client = slack.WebClient(
            token="xoxp-1234",
            base_url="http://localhost:8888",
        )
        self.async_client = slack.WebClient(
            token="xoxp-1234",
            run_async=True,
            base_url="http://localhost:8888",
        )

    def tearDown(self):
        cleanup_mock_web_api_server(self)

    pattern_for_language = re.compile("python/(\\S+)", re.IGNORECASE)
    pattern_for_package_identifier = re.compile("slackclient/(\\S+)")

    def test_api_calls_return_a_response_when_run_in_sync_mode(self):
        self.client.token = "xoxb-api_test"
        resp = self.client.api_test()
        self.assertFalse(asyncio.isfuture(resp))
        self.assertTrue(resp["ok"])

    def test_api_calls_include_user_agent(self):
        self.client.token = "xoxb-api_test"
        resp = self.client.api_test()
        self.assertEqual(200, resp.status_code)

    @async_test
    async def test_api_calls_return_a_future_when_run_in_async_mode(self):
        self.client.token = "xoxb-api_test"
        self.client.run_async = True
        future = self.client.api_test()
        self.assertTrue(asyncio.isfuture(future))
        resp = await future
        self.assertEqual(200, resp.status_code)
        self.assertTrue(resp["ok"])

    def test_builtin_api_methods_send_json(self):
        self.client.token = "xoxb-api_test"
        resp = self.client.api_test(msg="bye")
        self.assertEqual(200, resp.status_code)
        self.assertEqual("bye", resp["args"]["msg"])

    def test_requests_can_be_paginated(self):
        self.client.token = "xoxb-users_list_pagination"
        users = []
        for page in self.client.users_list(limit=2):
            users = users + page["members"]
        self.assertTrue(len(users) == 4)

    def test_response_can_be_paginated_multiple_times(self):
        self.client.token = "xoxb-channels_list_pagination"
        # This test suite verifies the changes in #521 work as expected
        response = self.client.channels_list(limit=1)
        ids = []
        for page in response:
            ids.append(page["channels"][0]["id"])
        self.assertEqual(ids, ["C1", "C2", "C3"])

        # The second iteration starting with page 2
        # (page1 is already cached in `response`)
        self.client.token = "xoxb-channels_list_pagination2"
        ids = []
        for page in response:
            ids.append(page["channels"][0]["id"])
        self.assertEqual(ids, ["C1", "C2", "C3"])

    def test_request_pagination_stops_when_next_cursor_is_missing(self):
        self.client.token = "xoxb-users_list_pagination_1"
        users = []
        for page in self.client.users_list(limit=2):
            users = users + page["members"]
        self.assertTrue(len(users) == 2)

    def test_json_can_only_be_sent_with_post_requests(self):
        with self.assertRaises(err.SlackRequestError):
            self.client.api_call("fake.method", http_verb="GET", json={})

    def test_slack_api_error_is_raised_on_unsuccessful_responses(self):
        self.client.token = "xoxb-api_test_false"
        with self.assertRaises(err.SlackApiError):
            self.client.api_test()
        self.client.token = "xoxb-500"
        with self.assertRaises(err.SlackApiError):
            self.client.api_test()

    def test_slack_api_rate_limiting_exception_returns_retry_after(self):
        self.client.token = "xoxb-rate_limited"
        try:
            self.client.api_test()
        except Exception as slack_api_error:
            self.assertFalse(slack_api_error.response["ok"])
            self.assertEqual(429, slack_api_error.response.status_code)
            self.assertEqual(30, int(slack_api_error.response.headers["Retry-After"]))

    def test_the_api_call_files_argument_creates_the_expected_data(self):
        self.client.token = "xoxb-users_setPhoto"
        resp = self.client.users_setPhoto(image="tests/data/slack_logo.png")
        self.assertEqual(200, resp.status_code)

    def test_issue_560_bool_in_params_sync(self):
        self.client.token = "xoxb-conversations_list"
        self.client.conversations_list(exclude_archived=1)  # ok
        self.client.conversations_list(exclude_archived="true")  # ok
        self.client.conversations_list(exclude_archived=True)  # ok

    @async_test
    async def test_issue_560_bool_in_params_async(self):
        self.async_client.token = "xoxb-conversations_list"
        await self.async_client.conversations_list(exclude_archived=1)  # ok
        await self.async_client.conversations_list(exclude_archived="true")  # ok
        await self.async_client.conversations_list(exclude_archived=True)  # TypeError

    def test_urlib_client_invalid_url(self):
        client = UrllibWebClient(token = "xoxb-xxxx")
        with self.assertRaises(err.SlackRequestError):
            client.api_call(url="file:///Users/alice/.bash_profile")
