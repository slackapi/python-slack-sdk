import asyncio
import logging
import os
import unittest

import pytest

from integration_tests.env_variable_names import SLACK_SDK_TEST_BOT_TOKEN
from integration_tests.helpers import async_test, is_not_specified
from slack import WebClient


class TestWebClient(unittest.TestCase):
    """Runs integration tests with real Slack API

    https://github.com/slackapi/python-slackclient/issues/560
    """

    def setUp(self):
        self.logger = logging.getLogger(__name__)
        self.bot_token = os.environ[SLACK_SDK_TEST_BOT_TOKEN]
        self.sync_client: WebClient = WebClient(token=self.bot_token, run_async=False, loop=asyncio.new_event_loop())
        self.async_client: WebClient = WebClient(token=self.bot_token, run_async=True)

    def tearDown(self):
        pass

    def test_issue_560_success(self):
        client = self.sync_client
        response = client.conversations_list(exclude_archived=1)
        self.assertIsNotNone(response)

        response = client.conversations_list(exclude_archived="true")
        self.assertIsNotNone(response)

    @pytest.mark.skipif(condition=is_not_specified(), reason="still unfixed")
    def test_issue_560_failure(self):
        client = self.sync_client
        response = client.conversations_list(exclude_archived=True)
        self.assertIsNotNone(response)

    @pytest.mark.skipif(condition=is_not_specified(), reason="still unfixed")
    @async_test
    async def test_issue_560_failure_async(self):
        client = self.async_client
        response = await client.conversations_list(exclude_archived=True)
        self.assertIsNotNone(response)

    # _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
    #
    # v = True
    #
    #     @staticmethod
    #     def _query_var(v):
    #         if isinstance(v, str):
    #             return v
    #         if type(v) is int:  # no subclasses like bool
    #             return str(v)
    # >       raise TypeError(
    #             "Invalid variable type: value "
    #             "should be str or int, got {!r} "
    #             "of type {}".format(v, type(v))
    #         )
    # E       TypeError: Invalid variable type: value should be str or int, got True of type <class 'bool'>
    #
    # path-to-python/site-packages/yarl/__init__.py:824: TypeError
    # -------------------------------------------------------------------------------------------------- Captured log call --------------------------------------------------------------------------------------------------
