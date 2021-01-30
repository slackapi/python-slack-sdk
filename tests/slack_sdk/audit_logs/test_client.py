import unittest

from slack_sdk.audit_logs.client import AuditLogsClient
from slack_sdk.audit_logs.response import AuditLogsResponse
from tests.slack_sdk.audit_logs.mock_web_api_server import (
    cleanup_mock_web_api_server,
    setup_mock_web_api_server,
)


class TestAuditLogsClient(unittest.TestCase):
    def setUp(self):
        self.client = AuditLogsClient(token="xoxp-", base_url="http://localhost:8888/")
        setup_mock_web_api_server(self)

    def tearDown(self):
        cleanup_mock_web_api_server(self)

    def test_logs(self):
        resp: AuditLogsResponse = self.client.logs(limit=1, action="user_login")
        self.assertEqual(200, resp.status_code)
        self.assertIsNotNone(resp.body.get("entries"))

    def test_actions(self):
        resp: AuditLogsResponse = self.client.actions()
        self.assertEqual(200, resp.status_code)
        self.assertIsNotNone(resp.body.get("actions"))

    def test_schemas(self):
        resp: AuditLogsResponse = self.client.schemas()
        self.assertEqual(200, resp.status_code)
        self.assertIsNotNone(resp.body.get("schemas"))
