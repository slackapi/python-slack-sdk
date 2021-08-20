import unittest

from slack_sdk.web.async_slack_response import AsyncSlackResponse
from slack_sdk.web.async_client import AsyncWebClient


class TestAsyncSlackResponse(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    # https://github.com/slackapi/python-slack-sdk/issues/1100
    def test_issue_1100(self):
        response = AsyncSlackResponse(
            client=AsyncWebClient(token="xoxb-dummy"),
            http_verb="POST",
            api_url="http://localhost:3000/api.test",
            req_args={},
            data=None,
            headers={},
            status_code=200,
        )
        with self.assertRaises(ValueError):
            response["foo"]

        foo = response.get("foo")
        self.assertIsNone(foo)

    # https://github.com/slackapi/python-slack-sdk/issues/1102
    def test_issue_1102(self):
        response = AsyncSlackResponse(
            client=AsyncWebClient(token="xoxb-dummy"),
            http_verb="POST",
            api_url="http://localhost:3000/api.test",
            req_args={},
            data={"ok": True, "args": {"hello": "world"}},
            headers={},
            status_code=200,
        )
        self.assertTrue("ok" in response)
        self.assertTrue("foo" not in response)
