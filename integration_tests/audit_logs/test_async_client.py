import os
import unittest

from integration_tests.env_variable_names import (
    SLACK_SDK_TEST_GRID_ORG_ADMIN_USER_TOKEN,
)
from integration_tests.helpers import async_test
from slack_sdk.audit_logs.async_client import AsyncAuditLogsClient


class TestAuditLogsClient(unittest.TestCase):
    def setUp(self):
        self.client = AsyncAuditLogsClient(token=os.environ[SLACK_SDK_TEST_GRID_ORG_ADMIN_USER_TOKEN])

    def tearDown(self):
        pass

    @async_test
    async def test_api_call(self):
        api_response = await self.client.api_call(path="schemas")
        self.assertEqual(200, api_response.status_code)
        self.assertTrue(api_response.raw_body.startswith("""{"schemas":[{"""))
        self.assertIsNotNone(api_response.body.get("schemas"))

    @async_test
    async def test_schemas(self):
        api_response = await self.client.schemas()
        self.assertEqual(200, api_response.status_code)
        self.assertTrue(api_response.raw_body.startswith("""{"schemas":[{"""))
        self.assertIsNotNone(api_response.body.get("schemas"))

    @async_test
    async def test_actions(self):
        api_response = await self.client.actions()
        self.assertEqual(200, api_response.status_code)
        self.assertTrue(api_response.raw_body.startswith("""{"actions":{"""))
        self.assertIsNotNone(api_response.body.get("actions"))

    @async_test
    async def test_logs(self):
        api_response = await self.client.logs(action="user_login", limit=1)
        self.assertEqual(200, api_response.status_code)
        self.assertTrue(api_response.raw_body.startswith("""{"entries":[{"""))
        self.assertIsNotNone(api_response.body.get("entries"))
