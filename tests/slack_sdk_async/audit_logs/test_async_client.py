import unittest

from slack_sdk.audit_logs.async_client import AsyncAuditLogsClient
from slack_sdk.audit_logs import AuditLogsResponse
from tests.helpers import async_test
from tests.slack_sdk.audit_logs.mock_web_api_server import (
    cleanup_mock_web_api_server,
    setup_mock_web_api_server,
)


class TestAsyncAuditLogsClient(unittest.TestCase):
    def setUp(self):
        self.client = AsyncAuditLogsClient(token="xoxp-", base_url="http://localhost:8888/")
        setup_mock_web_api_server(self)

    def tearDown(self):
        cleanup_mock_web_api_server(self)

    @async_test
    async def test_logs(self):
        resp: AuditLogsResponse = await self.client.logs(limit=1, action="user_login")
        self.assertEqual(200, resp.status_code)
        self.assertIsNotNone(resp.body.get("entries"))

        self.assertEqual(resp.typed_body.entries[0].id, "xxx-yyy-zzz-111")

    @async_test
    async def test_logs_pagination(self):
        resp: AuditLogsResponse = await self.client.logs(limit=1, action="user_login", cursor="XXXXXXXXXXX")
        self.assertEqual(200, resp.status_code)
        self.assertIsNotNone(resp.body.get("entries"))

        self.assertEqual(resp.typed_body.entries[0].id, "xxx-yyy-zzz-111")

    @async_test
    async def test_actions(self):
        resp: AuditLogsResponse = await self.client.actions()
        self.assertEqual(200, resp.status_code)
        self.assertIsNotNone(resp.body.get("actions"))

    @async_test
    async def test_schemas(self):
        resp: AuditLogsResponse = await self.client.schemas()
        self.assertEqual(200, resp.status_code)
        self.assertIsNotNone(resp.body.get("schemas"))
