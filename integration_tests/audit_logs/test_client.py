import os
import unittest

from integration_tests.env_variable_names import (
    SLACK_SDK_TEST_GRID_ORG_ADMIN_USER_TOKEN,
)
from slack_sdk.audit_logs import AuditLogsClient


class TestAuditLogsClient(unittest.TestCase):
    def setUp(self):
        self.client = AuditLogsClient(token=os.environ[SLACK_SDK_TEST_GRID_ORG_ADMIN_USER_TOKEN])

    def tearDown(self):
        pass

    def test_api_call(self):
        api_response = self.client.api_call(path="schemas")
        self.assertEqual(200, api_response.status_code)
        self.assertTrue(api_response.raw_body.startswith("""{"schemas":[{"""))
        self.assertIsNotNone(api_response.body.get("schemas"))

    def test_schemas(self):
        api_response = self.client.schemas()
        self.assertEqual(200, api_response.status_code)
        self.assertTrue(api_response.raw_body.startswith("""{"schemas":[{"""))
        self.assertIsNotNone(api_response.body.get("schemas"))

    def test_actions(self):
        api_response = self.client.actions()
        self.assertEqual(200, api_response.status_code)
        self.assertTrue(api_response.raw_body.startswith("""{"actions":{"""))
        self.assertIsNotNone(api_response.body.get("actions"))

    def test_logs(self):
        api_response = self.client.logs(action="user_login", limit=1)
        self.assertEqual(200, api_response.status_code)
        self.assertTrue(api_response.raw_body.startswith("""{"entries":[{"""))
        self.assertIsNotNone(api_response.body.get("entries"))
