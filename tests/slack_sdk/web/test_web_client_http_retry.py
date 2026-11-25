import logging
import unittest
from unittest.mock import patch

from slack_sdk.errors import SlackApiError
from slack_sdk.http_retry import RateLimitErrorRetryHandler
from slack_sdk.web import WebClient
from tests.slack_sdk.web.mock_web_api_handler import MockHandler
from tests.mock_web_api_server import setup_mock_web_api_server, cleanup_mock_web_api_server
from ..fatal_error_retry_handler import FatalErrorRetryHandler
from ..my_retry_handler import MyRetryHandler


class TestWebClient_HttpRetry(unittest.TestCase):
    def setUp(self):
        setup_mock_web_api_server(self, MockHandler)

    def tearDown(self):
        cleanup_mock_web_api_server(self)

    def test_remote_disconnected(self):
        retry_handler = MyRetryHandler(max_retry_count=2)
        client = WebClient(
            base_url="http://localhost:8888",
            token="xoxb-remote_disconnected",
            team_id="T111",
            retry_handlers=[retry_handler],
        )
        try:
            client.auth_test()
            self.fail("An exception is expected")
        except Exception as _:
            pass

        self.assertEqual(2, retry_handler.call_count)

    def test_ratelimited_no_retry(self):
        client = WebClient(
            base_url="http://localhost:8888",
            token="xoxb-ratelimited",
            team_id="T111",
        )
        try:
            client.auth_test()
            self.fail("An exception is expected")
        except SlackApiError as e:
            # Just running retries; no assertions for call count so far
            self.assertEqual(429, e.response.status_code)

    def test_ratelimited(self):
        client = WebClient(
            base_url="http://localhost:8888",
            token="xoxb-ratelimited_only_once",
            team_id="T111",
        )
        client.retry_handlers.append(RateLimitErrorRetryHandler())
        # The auto-retry should work here
        client.auth_test()

    def test_fatal_error_no_retry(self):
        client = WebClient(
            base_url="http://localhost:8888",
            token="xoxb-fatal_error",
            team_id="T111",
        )
        try:
            client.auth_test()
            self.fail("An exception is expected")
        except SlackApiError as e:
            # Just running retries; no assertions for call count so far
            self.assertEqual(200, e.response.status_code)
            self.assertEqual("fatal_error", e.response["error"])

    def test_fatal_error(self):
        client = WebClient(
            base_url="http://localhost:8888",
            token="xoxb-fatal_error_only_once",
            team_id="T111",
        )
        client.retry_handlers.append(FatalErrorRetryHandler())
        # The auto-retry should work here
        client.auth_test()

    def ratelimited_client(self, logger: logging.Logger) -> WebClient:
        return WebClient(
            base_url="http://localhost:8888",
            token="xoxb-ratelimited",
            team_id="T111",
            logger=logger,
            retry_handlers=[RateLimitErrorRetryHandler(max_retry_count=1)],
        )

    def test_retry_is_logged_at_debug(self):
        logger = logging.getLogger(f"{__name__}.retry_debug")
        client = self.ratelimited_client(logger)

        with self.assertLogs(logger, level=logging.DEBUG) as logs, self.assertRaises(SlackApiError):
            client.auth_test()

        retry_levels = [record.levelno for record in logs.records if "A retry handler found" in record.getMessage()]
        self.assertEqual(retry_levels, [logging.DEBUG])

    def test_retry_is_not_logged_at_info(self):
        parent = logging.getLogger(f"{__name__}.retry_info")
        client = self.ratelimited_client(logging.getLogger(f"{__name__}.retry_info.client"))

        with self.assertLogs(parent, level=logging.INFO) as logs, self.assertRaises(SlackApiError):
            parent.info("sentinel")
            client.auth_test()

        self.assertEqual(logs.output, [f"INFO:{parent.name}:sentinel"])

    def test_response_is_not_formatted_for_debug_when_debug_is_disabled(self):
        parent = logging.getLogger(f"{__name__}.debug_guard")
        parent.setLevel(logging.INFO)
        self.addCleanup(parent.setLevel, logging.NOTSET)
        logger = logging.getLogger(f"{__name__}.debug_guard.client")
        client = WebClient(base_url="http://localhost:8888", token="xoxb-api_test", team_id="T111", logger=logger)

        with patch.object(logger, "debug") as debug:
            client.auth_test()

        debug.assert_not_called()
