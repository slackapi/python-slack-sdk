import unittest
from urllib.error import URLError

from slack_sdk.audit_logs import AuditLogsClient, AuditLogsResponse
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

        self.assertEqual(resp.typed_body.entries[0].id, "xxx-yyy-zzz-111")

    def test_logs_pagination(self):
        resp: AuditLogsResponse = self.client.logs(limit=1, action="user_login", cursor="xxxxxxx")
        self.assertEqual(200, resp.status_code)
        self.assertIsNotNone(resp.body.get("entries"))

        self.assertEqual(resp.typed_body.entries[0].id, "xxx-yyy-zzz-111")

    def test_actions(self):
        resp: AuditLogsResponse = self.client.actions()
        self.assertEqual(200, resp.status_code)
        self.assertIsNotNone(resp.body.get("actions"))

    def test_schemas(self):
        resp: AuditLogsResponse = self.client.schemas()
        self.assertEqual(200, resp.status_code)
        self.assertIsNotNone(resp.body.get("schemas"))

    def test_url_error(self):
        invalid_url = "http://localhost:9999/"
        client = AuditLogsClient(token="xoxp-", base_url=invalid_url)
        with self.assertRaises(URLError):
            client.logs(limit=1, action="user_login")

    def test_http_error(self):
        resp: AuditLogsResponse = self.client.api_call(path="error")
        self.assertEqual(500, resp.status_code)
        self.assertEqual("unexpected response body", resp.raw_body)
