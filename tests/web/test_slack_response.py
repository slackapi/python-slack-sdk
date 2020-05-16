import unittest

from slack import WebClient
from slack.web.slack_response import SlackResponse


class TestSlackResponse(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    # https://github.com/slackapi/python-slackclient/issues/559
    def test_issue_559(self):
        response = SlackResponse(
            client=WebClient(token="xoxb-dummy"),
            http_verb="POST",
            api_url="http://localhost:3000/api.test",
            req_args={},
            data={
                "ok": True,
                "args": {
                    "hello": "world"
                }
            },
            headers={},
            status_code=200,
        )

        self.assertTrue("ok" in response.data)
        self.assertTrue("args" in response.data)
        self.assertFalse("error" in response.data)
