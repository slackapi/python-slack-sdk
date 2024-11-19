import re
import socket
import unittest
import time

import slack_sdk.errors as err
from slack_sdk import WebClient
from slack_sdk.models.blocks import DividerBlock
from slack_sdk.models.metadata import Metadata
from tests.slack_sdk.web.mock_web_api_server import (
    setup_mock_web_api_server,
    cleanup_mock_web_api_server,
)


class TestWebClient(unittest.TestCase):
    def setUp(self):
        setup_mock_web_api_server(self)
        self.client = WebClient(
            token="xoxb-api_test",
            base_url="http://localhost:8888",
        )

    def tearDown(self):
        cleanup_mock_web_api_server(self)

    pattern_for_language = re.compile("python/(\\S+)", re.IGNORECASE)
    pattern_for_package_identifier = re.compile("slackclient/(\\S+)")

    def test_subsequent_requests_with_a_session_succeeds(self):
        resp = self.client.api_test()
        assert resp["ok"]
        resp = self.client.api_test()
        assert resp["ok"]

    def test_api_calls_include_user_agent(self):
        self.client.token = "xoxb-api_test"
        resp = self.client.api_test()
        self.assertEqual(200, resp.status_code)

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
        self.client.token = "xoxb-conversations_list_pagination"
        # This test suite verifies the changes in #521 work as expected
        response = self.client.conversations_list(limit=1)
        ids = []
        for page in response:
            ids.append(page["channels"][0]["id"])
        self.assertEqual(ids, ["C1", "C2", "C3"])

        # The second iteration starting with page 2
        # (page1 is already cached in `response`)
        self.client.token = "xoxb-conversations_list_pagination2"
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
        self.client.token = "xoxb-ratelimited"
        try:
            self.client.api_test()
        except err.SlackApiError as slack_api_error:
            self.assertFalse(slack_api_error.response["ok"])
            self.assertEqual(429, slack_api_error.response.status_code)
            self.assertEqual(1, int(slack_api_error.response.headers["retry-after"]))
            self.assertEqual(1, int(slack_api_error.response.headers["Retry-After"]))

    def test_the_api_call_files_argument_creates_the_expected_data(self):
        self.client.token = "xoxb-users_setPhoto"
        resp = self.client.users_setPhoto(image="tests/slack_sdk_fixture/slack_logo.png")
        self.assertEqual(200, resp.status_code)

    def test_issue_560_bool_in_params_sync(self):
        self.client.token = "xoxb-conversations_list"
        self.client.conversations_list(exclude_archived=1)  # ok
        self.client.conversations_list(exclude_archived="true")  # ok
        self.client.conversations_list(exclude_archived=True)  # ok

    def test_issue_690_oauth_v2_access(self):
        self.client.token = ""
        resp = self.client.oauth_v2_access(client_id="111.222", client_secret="secret", code="codeeeeeeeeee")
        self.assertIsNone(resp["error"])
        with self.assertRaises(err.SlackApiError):
            self.client.oauth_v2_access(client_id="999.999", client_secret="secret", code="codeeeeeeeeee")

    def test_issue_690_oauth_access(self):
        self.client.token = ""
        resp = self.client.oauth_access(client_id="111.222", client_secret="secret", code="codeeeeeeeeee")
        self.assertIsNone(resp["error"])
        with self.assertRaises(err.SlackApiError):
            self.client.oauth_access(client_id="999.999", client_secret="secret", code="codeeeeeeeeee")

    def test_issue_705_no_param_request_pagination(self):
        self.client.token = "xoxb-users_list_pagination"
        users = []
        for page in self.client.users_list():
            users = users + page["members"]
        self.assertTrue(len(users) == 4)

    def test_token_param(self):
        client = WebClient(base_url="http://localhost:8888")
        with self.assertRaises(err.SlackApiError):
            client.users_list()
        resp = client.users_list(token="xoxb-users_list_pagination")
        self.assertIsNone(resp["error"])
        with self.assertRaises(err.SlackApiError):
            client.users_list()

    def test_timeout_issue_712(self):
        client = WebClient(base_url="http://localhost:8888", timeout=1)
        with self.assertRaises(socket.timeout):
            client.users_list(token="xoxb-timeout")

    def test_html_response_body_issue_718(self):
        client = WebClient(base_url="http://localhost:8888")
        try:
            client.users_list(token="xoxb-html_response")
            self.fail("SlackApiError expected here")
        except err.SlackApiError as e:
            self.assertTrue(
                str(e).startswith("The request to the Slack API failed. (url: http://"),
                e,
            )

    def test_user_agent_customization_issue_769(self):
        client = WebClient(
            base_url="http://localhost:8888",
            token="xoxb-user-agent this_is test",
            user_agent_prefix="this_is",
            user_agent_suffix="test",
        )
        resp = client.api_test()
        self.assertTrue(resp["ok"])

    def test_default_team_id(self):
        client = WebClient(base_url="http://localhost:8888", team_id="T_DEFAULT")
        resp = client.users_list(token="xoxb-users_list_pagination")
        self.assertIsNone(resp["error"])

    def test_message_metadata(self):
        client = self.client
        new_message = client.chat_postMessage(
            channel="#random",
            text="message with metadata",
            metadata=Metadata(
                event_type="procurement-task",
                event_payload={
                    "id": "11111",
                    "amount": 5000,
                    "tags": ["foo", "bar", "baz"],
                },
            ),
        )
        self.assertIsNone(new_message.get("error"))

        history = client.conversations_history(
            channel=new_message.get("channel"),
            limit=1,
            include_all_metadata=True,
        )
        self.assertIsNone(history.get("error"))

        modification = client.chat_update(
            channel=new_message.get("channel"),
            ts=new_message.get("ts"),
            text="message with metadata (modified)",
            metadata=Metadata(
                event_type="procurement-task",
                event_payload={
                    "id": "11111",
                    "amount": 6000,
                },
            ),
        )
        self.assertIsNone(modification.get("error"))

        scheduled = client.chat_scheduleMessage(
            channel=new_message.get("channel"),
            post_at=int(time.time()) + 30,
            text="message with metadata (scheduled)",
            metadata=Metadata(
                event_type="procurement-task",
                event_payload={
                    "id": "11111",
                    "amount": 10,
                },
            ),
        )
        self.assertIsNone(scheduled.get("error"))

    def test_user_auth_blocks(self):
        client = self.client
        new_message = client.chat_unfurl(
            channel="C12345",
            ts="1111.2222",
            unfurls={},
            user_auth_blocks=[DividerBlock(), DividerBlock()],
        )
        self.assertIsNone(new_message.get("error"))
