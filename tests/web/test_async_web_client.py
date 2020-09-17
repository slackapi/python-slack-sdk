import io
import re
import unittest

import slack.errors as err
from slack import AsyncWebClient
from tests.helpers import async_test
from tests.web.mock_web_api_server import setup_mock_web_api_server, cleanup_mock_web_api_server


class TestAsyncWebClient(unittest.TestCase):

    def setUp(self):
        setup_mock_web_api_server(self)
        self.client = AsyncWebClient(
            token="xoxp-1234",
            base_url="http://localhost:8888",
        )

    def tearDown(self):
        cleanup_mock_web_api_server(self)

    pattern_for_language = re.compile("python/(\\S+)", re.IGNORECASE)
    pattern_for_package_identifier = re.compile("slackclient/(\\S+)")

    @async_test
    async def test_api_calls_return_a_future(self):
        self.client.token = "xoxb-api_test"
        resp = await self.client.api_test()
        self.assertEqual(200, resp.status_code)
        self.assertTrue(resp["ok"])

    @async_test
    async def test_requests_can_be_paginated(self):
        self.client.token = "xoxb-users_list_pagination"
        users = []
        async for page in await self.client.users_list(limit=2):
            users = users + page["members"]
        self.assertTrue(len(users) == 4)

    @async_test
    async def test_request_pagination_stops_when_next_cursor_is_missing(self):
        self.client.token = "xoxb-users_list_pagination_1"
        users = []
        async for page in await self.client.users_list(limit=2):
            users = users + page["members"]
        self.assertTrue(len(users) == 2)

    @async_test
    async def test_json_can_only_be_sent_with_post_requests(self):
        with self.assertRaises(err.SlackRequestError):
            await self.client.api_call("fake.method", http_verb="GET", json={})

    @async_test
    async def test_slack_api_error_is_raised_on_unsuccessful_responses(self):
        self.client.token = "xoxb-api_test_false"
        with self.assertRaises(err.SlackApiError):
            await self.client.api_test()
        self.client.token = "xoxb-500"
        with self.assertRaises(err.SlackApiError):
            await self.client.api_test()

    @async_test
    async def test_slack_api_rate_limiting_exception_returns_retry_after(self):
        self.client.token = "xoxb-rate_limited"
        try:
            await self.client.api_test()
        except err.SlackApiError as slack_api_error:
            self.assertFalse(slack_api_error.response["ok"])
            self.assertEqual(429, slack_api_error.response.status_code)
            self.assertEqual(30, int(slack_api_error.response.headers["Retry-After"]))

    @async_test
    async def test_the_api_call_files_argument_creates_the_expected_data(self):
        self.client.token = "xoxb-users_setPhoto"
        resp = await self.client.users_setPhoto(image="tests/data/slack_logo.png")
        self.assertEqual(200, resp.status_code)

    @async_test
    async def test_issue_560_bool_in_params_sync(self):
        self.client.token = "xoxb-conversations_list"
        await self.client.conversations_list(exclude_archived=1)  # ok
        await self.client.conversations_list(exclude_archived="true")  # ok
        await self.client.conversations_list(exclude_archived=True)  # ok

    @async_test
    async def test_issue_690_oauth_v2_access_async(self):
        self.client.token = ""
        resp = await self.client.oauth_v2_access(
            client_id="111.222",
            client_secret="secret",
            code="codeeeeeeeeee",
        )
        self.assertIsNone(resp["error"])
        with self.assertRaises(err.SlackApiError):
            await self.client.oauth_v2_access(
                client_id="999.999",
                client_secret="secret",
                code="codeeeeeeeeee",
            )

    @async_test
    async def test_issue_690_oauth_access_async(self):
        self.client.token = ""
        resp = await self.client.oauth_access(client_id="111.222", client_secret="secret", code="codeeeeeeeeee")
        self.assertIsNone(resp["error"])
        with self.assertRaises(err.SlackApiError):
            await self.client.oauth_access(client_id="999.999", client_secret="secret", code="codeeeeeeeeee")

    @async_test
    async def test_token_param_async(self):
        with self.assertRaises(err.SlackApiError):
            await self.client.users_list()
        resp = await self.client.users_list(token="xoxb-users_list_pagination")
        self.assertIsNone(resp["error"])
        with self.assertRaises(err.SlackApiError):
            await self.client.users_list()

    @async_test
    async def test_timeout_issue_712_async(self):
        with self.assertRaises(Exception):
            await self.client.users_list(token="xoxb-timeout")

    @async_test
    async def test_html_response_body_issue_718_async(self):
        try:
            await self.client.users_list(token="xoxb-html_response")
            self.fail("SlackApiError expected here")
        except err.SlackApiError as e:
            self.assertTrue(
                str(e).startswith("Failed to parse the response body: Expecting value: line 1 column 1 (char 0)"), e)

    @async_test
    async def test_user_agent_customization_issue_769_async(self):
        client = AsyncWebClient(
            token="xoxb-user-agent this_is test",
            base_url="http://localhost:8888",
            user_agent_prefix="this_is",
            user_agent_suffix="test",
        )
        resp = await client.api_test()
        self.assertTrue(resp["ok"])

    @async_test
    async def test_issue_809_filename_for_IOBase(self):
        self.client.token = "xoxb-api_test"
        file = io.BytesIO(b'here is my data but not sure what is wrong.......')
        resp = await self.client.files_upload(file=file)
        self.assertIsNone(resp["error"])
        #         if file:
        #             if "filename" not in kwargs:
        #                 # use the local filename if filename is missing
        # >               kwargs["filename"] = file.split(os.path.sep)[-1]
        # E               AttributeError: '_io.BytesIO' object has no attribute 'split'
