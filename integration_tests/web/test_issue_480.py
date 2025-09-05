import logging
import multiprocessing
import os
import threading
import unittest

from integration_tests.env_variable_names import SLACK_SDK_TEST_USER_TOKEN
from integration_tests.helpers import async_test
from slack_sdk.web import WebClient
from slack_sdk.web.async_client import AsyncWebClient


class TestWebClient(unittest.TestCase):
    """Runs integration tests with real Slack API
    https://github.com/slackapi/python-slack-sdk/issues/480
    """

    def setUp(self):
        self.logger = logging.getLogger(__name__)
        self.user_token = os.environ[SLACK_SDK_TEST_USER_TOKEN]
        self.sync_client: WebClient = WebClient(token=self.user_token)
        self.async_client: AsyncWebClient = AsyncWebClient(token=self.user_token)

    def tearDown(self):
        pass

    def test_issue_480_processes(self):
        client = self.sync_client
        before = len(multiprocessing.active_children())
        for idx in range(10):
            response = client.api_test()
            self.assertIsNotNone(response)
        after = len(multiprocessing.active_children())
        self.assertEqual(0, after - before)

    @async_test
    async def test_issue_480_processes_async(self):
        client = self.async_client
        before = len(multiprocessing.active_children())
        for idx in range(10):
            response = await client.api_test()
            self.assertIsNotNone(response)
        after = len(multiprocessing.active_children())
        self.assertEqual(0, after - before)

    # fails with Python 3.6
    def test_issue_480_threads(self):
        client = self.sync_client
        before = threading.active_count()
        for idx in range(10):
            response = client.api_test()
            self.assertIsNotNone(response)
        after = threading.active_count()
        self.assertEqual(0, after - before)

    # fails with Python 3.6
    @async_test
    async def test_issue_480_threads_async(self):
        client = self.async_client
        before = threading.active_count()
        for idx in range(10):
            response = await client.api_test()
            self.assertIsNotNone(response)
        after = threading.active_count()
        self.assertEqual(0, after - before)
