import os
import unittest
import time

from integration_tests.env_variable_names import (
    SLACK_SDK_TEST_GRID_ORG_ADMIN_USER_TOKEN,
)
from slack_sdk.web import WebClient


class TestWebClient(unittest.TestCase):
    def setUp(self):
        self.org_admin_token = os.environ[SLACK_SDK_TEST_GRID_ORG_ADMIN_USER_TOKEN]
        self.client: WebClient = WebClient(token=self.org_admin_token)

    def tearDown(self):
        pass

    def test_no_args(self):
        response = self.client.admin_users_unsupportedVersions_export()
        self.assertIsNone(response.get("error"))

    def test_full_args(self):
        response = self.client.admin_users_unsupportedVersions_export(
            date_end_of_support=int(round(time.time())) + 60 * 60 * 24 * 120,
            date_sessions_started=0,
        )
        self.assertIsNone(response.get("error"))

    def test_full_args_str(self):
        response = self.client.admin_users_unsupportedVersions_export(
            date_end_of_support=str(int(round(time.time())) + 60 * 60 * 24 * 120),
            date_sessions_started="0",
        )
        self.assertIsNone(response.get("error"))
