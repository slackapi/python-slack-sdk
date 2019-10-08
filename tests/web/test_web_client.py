# Standard Imports
import unittest
from unittest import mock
import asyncio
import re


# Internal Imports
import slack
from tests.helpers import async_test, fake_req_args, mock_request
import slack.errors as err


@mock.patch("slack.WebClient._request", new_callable=mock_request)
class TestWebClient(unittest.TestCase):
    def setUp(self):
        self.client = slack.WebClient("xoxb-abc-123", loop=asyncio.get_event_loop())

    def tearDown(self):
        pass

    pattern_for_language = re.compile("python/(\\S+)", re.IGNORECASE)
    pattern_for_package_identifier = re.compile("slackclient/(\\S+)")

    def test_api_calls_return_a_response_when_run_in_sync_mode(self, mock_request):
        resp = self.client.api_test()
        self.assertFalse(asyncio.isfuture(resp))
        self.assertTrue(resp["ok"])

    def test_api_calls_include_user_agent(self, mock_request):
        self.client.api_test()
        mock_call_kwargs = mock_request.call_args[1]
        self.assertIn("req_args", mock_call_kwargs)
        mock_call_req_args = mock_call_kwargs["req_args"]
        self.assertIn("headers", mock_call_req_args)
        mock_call_headers = mock_call_req_args["headers"]
        self.assertIn("User-Agent", mock_call_headers)
        mock_call_user_agent = mock_call_headers["User-Agent"]
        self.assertRegex(
            mock_call_user_agent,
            self.pattern_for_package_identifier,
            "User Agent contains slackclient and version",
        )
        self.assertRegex(
            mock_call_user_agent,
            self.pattern_for_language,
            "User Agent contains Python and version",
        )

    @async_test
    async def test_api_calls_return_a_future_when_run_in_async_mode(self, mock_request):
        self.client.run_async = True
        future = self.client.api_test()
        self.assertTrue(asyncio.isfuture(future))
        resp = await future
        self.assertTrue(resp["ok"])

    def test_builtin_api_methods_send_json(self, mock_request):
        self.client.api_test(msg="bye")
        mock_request.assert_called_once_with(
            http_verb="POST",
            api_url="https://www.slack.com/api/api.test",
            req_args=fake_req_args(json={"msg": "bye"}),
        )

    def test_requests_can_be_paginated(self, mock_request):
        mock_request.response.side_effect = [
            {
                "data": {
                    "ok": True,
                    "members": ["Bob", "cat"],
                    "response_metadata": {"next_cursor": 1},
                },
                "status_code": 200,
                "headers": {},
            },
            {
                "data": {"ok": True, "members": ["Kevin", "dog"]},
                "status_code": 200,
                "headers": {},
            },
        ]

        users = []
        for page in self.client.users_list(limit=2):
            users = users + page["members"]
        self.assertTrue(len(users) == 4)

    def test_response_can_be_paginated_multiple_times(self, mock_request):
        # This test suite verifies the changes in #521 work as expected
        page1 = {
            "data": {
                "ok": True,
                "channels": [{"id": "C1"}],
                "response_metadata": {"next_cursor": "has_page2"},
            },
            "status_code": 200,
            "headers": {},
        }
        page2 = {
            "data": {
                "ok": True,
                "channels": [{"id": "C2"}],
                "response_metadata": {"next_cursor": "has_page3"},
            },
            "status_code": 200,
            "headers": {},
        }
        page3 = {
            "data": {"ok": True, "channels": [{"id": "C3"}]},
            "status_code": 200,
            "headers": {},
        }
        # The initial pagination
        mock_request.response.side_effect = [page1, page2, page3]
        response = self.client.channels_list(limit=1)
        ids = []
        for page in response:
            ids.append(page["channels"][0]["id"])
        self.assertEqual(ids, ["C1", "C2", "C3"])

        # The second iteration starting with page 2
        # (page1 is already cached in `response`)
        mock_request.response.side_effect = [page2, page3]
        ids = []
        for page in response:
            ids.append(page["channels"][0]["id"])
        self.assertEqual(ids, ["C1", "C2", "C3"])

    def test_request_pagination_stops_when_next_cursor_is_missing(self, mock_request):
        mock_request.response.side_effect = [
            {
                "data": {"ok": True, "members": ["Bob", "cat"]},
                "status_code": 200,
                "headers": {},
            },
            {
                "data": {"ok": True, "members": ["Kevin", "dog"]},
                "status_code": 200,
                "headers": {},
            },
        ]

        users = []
        for page in self.client.users_list(limit=2):
            users = users + page["members"]
        self.assertTrue(len(users) == 2)
        mock_request.assert_called_once_with(
            http_verb="GET",
            api_url="https://www.slack.com/api/users.list",
            req_args=fake_req_args(params={"limit": 2}),
        )

    def test_xoxb_token_validation(self, mock_request):
        with self.assertRaises(err.BotUserAccessError):
            # Channels can only be created with xoxa tokens.
            self.client.channels_create(name="test")

    def test_json_can_only_be_sent_with_post_requests(self, mock_request):
        with self.assertRaises(err.SlackRequestError):
            self.client.api_call("fake.method", http_verb="GET", json={})

    def test_slack_api_error_is_raised_on_unsuccessful_responses(self, mock_request):
        mock_request.response.side_effect = [
            {"data": {"ok": False}, "status_code": 200, "headers": {}},
            {"data": {"ok": True}, "status_code": 500, "headers": {}},
        ]
        with self.assertRaises(err.SlackApiError):
            self.client.api_test()
        with self.assertRaises(err.SlackApiError):
            self.client.api_test()

    def test_slack_api_rate_limiting_exception_returns_retry_after(self, mock_request):
        mock_request.response.side_effect = [
            {"data": {"ok": False}, "status_code": 429, "headers": {"Retry-After": 30}}
        ]
        with self.assertRaises(err.SlackApiError) as context:
            self.client.api_test()
        slack_api_error = context.exception
        self.assertFalse(slack_api_error.response["ok"])
        self.assertEqual(429, slack_api_error.response.status_code)
        self.assertEqual(30, slack_api_error.response.headers["Retry-After"])

    def test_the_api_call_files_argument_creates_the_expected_data(self, mock_request):
        self.client.token = "xoxa-123"
        with mock.patch("builtins.open", mock.mock_open(read_data="fake")):
            self.client.users_setPhoto(image="/fake/path")

        mock_request.assert_called_once_with(
            http_verb="POST",
            api_url="https://www.slack.com/api/users.setPhoto",
            req_args=fake_req_args(),
        )
