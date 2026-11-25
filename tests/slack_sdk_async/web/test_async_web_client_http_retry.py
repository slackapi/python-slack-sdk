import logging
import unittest
from unittest.mock import patch

import slack_sdk.errors as err
from slack_sdk.http_retry.builtin_async_handlers import AsyncRateLimitErrorRetryHandler, AsyncServerErrorRetryHandler
from slack_sdk.web.async_client import AsyncWebClient
from tests.slack_sdk_async.helpers import async_test
from tests.slack_sdk.web.mock_web_api_handler import MockHandler
from tests.mock_web_api_server import setup_mock_web_api_server_async, cleanup_mock_web_api_server_async
from ..fatal_error_retry_handler import FatalErrorRetryHandler
from ..my_retry_handler import MyRetryHandler
from ..error_recording_retry_handler import ErrorRecordingRetryHandler, error_statuses


class TestAsyncWebClient_HttpRetries(unittest.TestCase):
    def setUp(self):
        setup_mock_web_api_server_async(self, MockHandler)

    def tearDown(self):
        cleanup_mock_web_api_server_async(self)

    @async_test
    async def test_remote_disconnected(self):
        retry_handler = MyRetryHandler(max_retry_count=2)
        client = AsyncWebClient(
            base_url="http://localhost:8888",
            token="xoxb-remote_disconnected",
            team_id="T111",
            retry_handlers=[retry_handler],
        )
        try:
            await client.auth_test()
            self.fail("An exception is expected")
        except Exception as _:
            pass

        self.assertEqual(2, retry_handler.call_count)

    @async_test
    async def test_ratelimited_no_retry(self):
        client = AsyncWebClient(
            base_url="http://localhost:8888",
            token="xoxb-ratelimited",
            team_id="T111",
        )
        try:
            await client.auth_test()
            self.fail("An exception is expected")
        except err.SlackApiError as e:
            # Just running retries; no assertions for call count so far
            self.assertEqual(429, e.response.status_code)

    @async_test
    async def test_ratelimited(self):
        client = AsyncWebClient(
            base_url="http://localhost:8888",
            token="xoxb-ratelimited_only_once",
            team_id="T111",
        )
        client.retry_handlers.append(AsyncRateLimitErrorRetryHandler())
        # The auto-retry should work here
        await client.auth_test()

    @async_test
    async def test_fatal_error_no_retry(self):
        client = AsyncWebClient(
            base_url="http://localhost:8888",
            token="xoxb-fatal_error",
            team_id="T111",
        )
        try:
            await client.auth_test()
            self.fail("An exception is expected")
        except err.SlackApiError as e:
            self.assertEqual("fatal_error", e.response["error"])

    @async_test
    async def test_fatal_error(self):
        client = AsyncWebClient(
            base_url="http://localhost:8888",
            token="xoxb-fatal_error_only_once",
            team_id="T111",
        )
        client.retry_handlers.append(FatalErrorRetryHandler())
        # The auto-retry should work here
        await client.auth_test()

    @async_test
    async def test_retries(self):
        retry_handler = MyRetryHandler(max_retry_count=2)
        client = AsyncWebClient(
            token="xoxp-remote_disconnected",
            base_url="http://localhost:8888",
            retry_handlers=[retry_handler],
        )
        try:
            await client.auth_test()
            self.fail("An exception is expected")
        except Exception as _:
            pass

        self.assertEqual(2, retry_handler.call_count)

    @async_test
    async def test_server_error(self):
        client = AsyncWebClient(
            base_url="http://localhost:8888",
            token="xoxb-server_error_only_once",
            team_id="T111",
        )
        client.retry_handlers.append(AsyncServerErrorRetryHandler())
        # The auto-retry should work here
        await client.chat_postMessage(channel="C123", text="Hi there!")

    @async_test
    async def test_server_error_passes_the_status_error_to_handlers(self):
        MockHandler.state["server_error_count"] = 0
        retry_handler = ErrorRecordingRetryHandler()
        client = AsyncWebClient(
            base_url="http://localhost:8888",
            token="xoxb-server_error_only_once",
            team_id="T111",
            retry_handlers=[retry_handler],
        )

        await client.chat_postMessage(channel="C123", text="Hi there!")

        self.assertEqual([500], error_statuses(retry_handler.can_retry_errors))
        self.assertEqual([500], error_statuses(retry_handler.prepare_errors))

    @async_test
    async def test_response_is_not_formatted_for_debug_when_debug_is_disabled(self):
        parent = logging.getLogger(f"{__name__}.debug_guard")
        parent.setLevel(logging.INFO)
        self.addCleanup(parent.setLevel, logging.NOTSET)
        logger = logging.getLogger(f"{__name__}.debug_guard.client")
        client = AsyncWebClient(base_url="http://localhost:8888", token="xoxb-api_test", team_id="T111", logger=logger)

        with patch.object(logger, "debug") as debug:
            await client.auth_test()

        debug.assert_not_called()

    @async_test
    async def test_ratelimited_retry_is_logged_at_info(self):
        parent = logging.getLogger(f"{__name__}.retry_info")
        client = AsyncWebClient(
            base_url="http://localhost:8888",
            token="xoxb-ratelimited",
            team_id="T111",
            logger=logging.getLogger(f"{parent.name}.client"),
            retry_handlers=[AsyncRateLimitErrorRetryHandler(max_retry_count=1)],
        )

        with self.assertLogs(parent, level=logging.INFO) as logs, self.assertRaises(err.SlackApiError):
            parent.info("sentinel")
            await client.auth_test()

        self.assertEqual(
            logs.output,
            [
                f"INFO:{parent.name}:sentinel",
                f"INFO:{parent.name}.client:Going to retry the same request: POST http://localhost:8888/auth.test",
            ],
        )
