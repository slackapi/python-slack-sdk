import unittest
from unittest.mock import patch

from slack_sdk.errors import SlackApiError
from slack_sdk.http_retry.builtin_handlers import RateLimitErrorRetryHandler
from slack_sdk.web import WebClient


class TestWebClient_MalformedJsonBody(unittest.TestCase):
    """A 200 response whose body looks like JSON but is truncated must surface as a SlackApiError,
    no matter whether retry handlers are configured."""

    malformed_response = {"status": 200, "headers": {}, "body": '{"ok": tru'}

    def _assert_non_json_error(self, client: WebClient):
        with patch.object(client, "_perform_urllib_http_request_internal", return_value=dict(self.malformed_response)):
            with self.assertRaises(SlackApiError) as ctx:
                client.api_test()
        self.assertTrue(ctx.exception.response["error"].startswith("Received a response in a non-JSON format"))

    def test_default_retry_handlers(self):
        self._assert_non_json_error(WebClient(token="xoxb-test"))

    def test_custom_retry_handlers(self):
        self._assert_non_json_error(WebClient(token="xoxb-test", retry_handlers=[RateLimitErrorRetryHandler()]))

    def test_no_retry_handlers(self):
        self._assert_non_json_error(WebClient(token="xoxb-test", retry_handlers=[]))

    def test_well_formed_json_body_is_still_parsed(self):
        client = WebClient(token="xoxb-test")
        response = {"status": 200, "headers": {}, "body": '{"ok": true}'}
        with patch.object(client, "_perform_urllib_http_request_internal", return_value=response):
            self.assertTrue(client.api_test()["ok"])
