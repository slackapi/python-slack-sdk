import unittest

import slack_sdk.errors as err
from slack_sdk.http_retry import RetryHandler, RetryIntervalCalculator
from slack_sdk.http_retry.builtin_handlers import ServerErrorRetryHandler
from slack_sdk.http_retry.handler import default_interval_calculator
from slack_sdk.web import WebClient
from tests.slack_sdk.web.mock_web_api_server import (
    setup_mock_web_api_server,
    cleanup_mock_web_api_server,
)


class MyServerErrorRetryHandler(RetryHandler):
    """RetryHandler that does retries for server-side errors."""

    def __init__(
        self,
        max_retry_count: int = 1,
        interval_calculator: RetryIntervalCalculator = default_interval_calculator,
    ):
        super().__init__(max_retry_count, interval_calculator)
        self.call_count = 0

    def _can_retry(
        self,
        *,
        state,
        request,
        response,
        error,
    ) -> bool:
        self.call_count += 1
        return response is not None and response.status_code >= 500


class TestWebClient_HttpRetry_ServerError(unittest.TestCase):
    def setUp(self):
        setup_mock_web_api_server(self)

    def tearDown(self):
        cleanup_mock_web_api_server(self)

    def test_html_response_body_issue_829(self):
        retry_handlers = [MyServerErrorRetryHandler(max_retry_count=2)]
        client = WebClient(
            base_url="http://localhost:8888",
            retry_handlers=retry_handlers,
        )
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

        self.assertEqual(2, retry_handlers[0].call_count)

    def test_server_error_using_built_in_handler(self):
        retry_handlers = [ServerErrorRetryHandler()]
        client = WebClient(
            base_url="http://localhost:8888",
            retry_handlers=retry_handlers,
        )
        client.users_list(token="xoxb-server_error_only_once")
