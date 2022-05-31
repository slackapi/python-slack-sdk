import logging
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

    def test_pagination(self):
        call_count = 0
        response = None
        ids = []
        while call_count < 10 and (response is None or response.status_code != 429):
            cursor = response.body["response_metadata"]["next_cursor"] if response is not None else None
            response = self.client.logs(action="user_login", limit=1, cursor=cursor)
            ids += map(lambda v: v["id"], response.body.get("entries", []))
            call_count += 1
        self.assertGreaterEqual(len(set(ids)), 10)
