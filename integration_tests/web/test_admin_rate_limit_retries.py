import logging
import os
import unittest

import pytest

from integration_tests.env_variable_names import (
    SLACK_SDK_TEST_GRID_ORG_ADMIN_USER_TOKEN,
)
from integration_tests.helpers import async_test, is_not_specified
from slack_sdk.http_retry import RateLimitErrorRetryHandler
from slack_sdk.http_retry.builtin_async_handlers import AsyncRateLimitErrorRetryHandler
from slack_sdk.web import WebClient
from slack_sdk.web.async_client import AsyncWebClient


class TestWebClient(unittest.TestCase):
    """Runs integration tests with real Slack API"""

    def setUp(self):
        self.logger = logging.getLogger(__name__)
        self.org_admin_token = os.environ[SLACK_SDK_TEST_GRID_ORG_ADMIN_USER_TOKEN]
        self.sync_client: WebClient = WebClient(token=self.org_admin_token)
        self.sync_client.retry_handlers.append(RateLimitErrorRetryHandler(max_retry_count=2))
        self.async_client: AsyncWebClient = AsyncWebClient(token=self.org_admin_token)
        self.async_client.retry_handlers.append(AsyncRateLimitErrorRetryHandler(max_retry_count=2))

    def tearDown(self):
        pass

    @pytest.mark.skipif(condition=is_not_specified(), reason="execution can take long")
    def test_sync(self):
        client = self.sync_client
        for response in client.admin_users_session_list(limit=1):
            self.assertIsNotNone(response.get("active_sessions"))

    @pytest.mark.skipif(condition=is_not_specified(), reason="execution can take long")
    @async_test
    async def test_async(self):
        client = self.async_client
        async for response in await client.admin_users_session_list(limit=1):
            self.assertIsNotNone(response.get("active_sessions"))
