# Standard Imports
import unittest
from unittest import mock

# import collections
# import signal

# ThirdParty Imports

# Internal Imports
import slack
from tests.helpers import mock_api_response, async_test, mock_req_args

# import slack.errors as e


@mock.patch("slack.WebClient._send", new_callable=mock_api_response)
class TestWebClient(unittest.TestCase):
    def setUp(self):
        self.client = slack.WebClient()

    def tearDown(self):
        pass

    def test_api_test(self, mock_api_response):
        self.client.api_test()
        mock_api_response.assert_called_once_with(
            http_verb="POST",
            api_url="https://www.slack.com/api/api.test",
            req_args=mock_req_args(),
        )

    def test_api_test_with_json(self, mock_api_response):
        self.client.api_test(msg="bye")
        mock_api_response.assert_called_once_with(
            http_verb="POST",
            api_url="https://www.slack.com/api/api.test",
            req_args=mock_req_args(json={"msg": "bye"}),
        )

    @async_test
    async def test_api_test_async_again(self, mock_api_response):
        self.client.run_async = True
        resp = await self.client.api_test()
        self.assertTrue(resp["ok"])
