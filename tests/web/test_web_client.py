import asyncio
import gc
import io
import re
import socket
import unittest

import slack.errors as err
from slack import WebClient
from tests.helpers import async_test
from tests.web.mock_web_api_server import setup_mock_web_api_server, cleanup_mock_web_api_server


class TestWebClient(unittest.TestCase):

    def setUp(self):
        setup_mock_web_api_server(self)
        self.client = WebClient(
            token="xoxp-1234",
            base_url="http://localhost:8888",
        )
        self.async_client = WebClient(
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

    def test_response_can_be_paginated_multiple_times_use_sync_aiohttp(self):
        self.client = WebClient(
            token="xoxp-1234",
            base_url="http://localhost:8888",
            run_async=False,
            use_sync_aiohttp=True,
        )
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
        except err.SlackApiError as slack_api_error:
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

    def test_issue_690_oauth_v2_access(self):
        self.client.token = ""
        resp = self.client.oauth_v2_access(client_id="111.222", client_secret="secret", code="codeeeeeeeeee")
        self.assertIsNone(resp["error"])
        with self.assertRaises(err.SlackApiError):
            self.client.oauth_v2_access(client_id="999.999", client_secret="secret", code="codeeeeeeeeee")

    @async_test
    async def test_issue_690_oauth_v2_access_async(self):
        self.async_client.token = ""
        resp = await self.async_client.oauth_v2_access(
            client_id="111.222",
            client_secret="secret",
            code="codeeeeeeeeee",
        )
        self.assertIsNone(resp["error"])
        with self.assertRaises(err.SlackApiError):
            await self.async_client.oauth_v2_access(
                client_id="999.999",
                client_secret="secret",
                code="codeeeeeeeeee",
            )

    def test_issue_690_oauth_access(self):
        self.client.token = ""
        resp = self.client.oauth_access(client_id="111.222", client_secret="secret", code="codeeeeeeeeee")
        self.assertIsNone(resp["error"])
        with self.assertRaises(err.SlackApiError):
            self.client.oauth_access(client_id="999.999", client_secret="secret", code="codeeeeeeeeee")

    @async_test
    async def test_issue_690_oauth_access_async(self):
        self.async_client.token = ""
        resp = await self.async_client.oauth_access(client_id="111.222", client_secret="secret", code="codeeeeeeeeee")
        self.assertIsNone(resp["error"])
        with self.assertRaises(err.SlackApiError):
            await self.async_client.oauth_access(client_id="999.999", client_secret="secret", code="codeeeeeeeeee")

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

    @async_test
    async def test_token_param_async(self):
        client = WebClient(base_url="http://localhost:8888", run_async=True)
        with self.assertRaises(err.SlackApiError):
            await client.users_list()
        resp = await client.users_list(token="xoxb-users_list_pagination")
        self.assertIsNone(resp["error"])
        with self.assertRaises(err.SlackApiError):
            await client.users_list()

    def test_timeout_issue_712(self):
        client = WebClient(base_url="http://localhost:8888", timeout=1)
        with self.assertRaises(socket.timeout):
            client.users_list(token="xoxb-timeout")

    @async_test
    async def test_timeout_issue_712_async(self):
        client = WebClient(base_url="http://localhost:8888", timeout=1, run_async=True)
        with self.assertRaises(asyncio.TimeoutError):
            await client.users_list(token="xoxb-timeout")

    def test_unclosed_client_session_issue_645_in_async_mode(self):
        def exception_handler(_, context):
            nonlocal session_unclosed
            if context["message"] == "Unclosed client session":
                session_unclosed = True

        async def issue_645():
            client = WebClient(base_url="http://localhost:8888", timeout=1, run_async=True)
            try:
                await client.users_list(token="xoxb-timeout")
            except asyncio.TimeoutError:
                pass

        session_unclosed = False
        loop = asyncio.get_event_loop()
        loop.set_exception_handler(exception_handler)
        loop.run_until_complete(issue_645())
        gc.collect()  # force Python to gc unclosed client session
        self.assertFalse(session_unclosed, "Unclosed client session")

    def test_html_response_body_issue_718(self):
        client = WebClient(base_url="http://localhost:8888")
        try:
            client.users_list(token="xoxb-html_response")
            self.fail("SlackApiError expected here")
        except err.SlackApiError as e:
            self.assertTrue(
                str(e).startswith("Failed to parse the response body: Expecting value: line 1 column 1 (char 0)"), e)

    @async_test
    async def test_html_response_body_issue_718_async(self):
        client = WebClient(base_url="http://localhost:8888", run_async=True)
        try:
            await client.users_list(token="xoxb-html_response")
            self.fail("SlackApiError expected here")
        except err.SlackApiError as e:
            self.assertTrue(
                str(e).startswith("Failed to parse the response body: Expecting value: line 1 column 1 (char 0)"), e)

    def test_user_agent_customization_issue_769(self):
        client = WebClient(
            base_url="http://localhost:8888",
            token="xoxb-user-agent this_is test",
            user_agent_prefix="this_is",
            user_agent_suffix="test",
        )
        resp = client.api_test()
        self.assertTrue(resp["ok"])

    @async_test
    async def test_user_agent_customization_issue_769_async(self):
        client = WebClient(
            run_async=True,
            base_url="http://localhost:8888",
            token="xoxb-user-agent this_is test",
            user_agent_prefix="this_is",
            user_agent_suffix="test",
        )
        resp = await client.api_test()
        self.assertTrue(resp["ok"])

    def test_issue_809_filename_for_IOBase(self):
        self.client.token = "xoxb-api_test"
        file = io.BytesIO(b'here is my data but not sure what is wrong.......')
        resp = self.client.files_upload(file=file)
        self.assertIsNone(resp["error"])
        #         if file:
        #             if "filename" not in kwargs:
        #                 # use the local filename if filename is missing
        # >               kwargs["filename"] = file.split(os.path.sep)[-1]
        # E               AttributeError: '_io.BytesIO' object has no attribute 'split'
