import json
import unittest

from slack_sdk.audit_logs.v1.logs import LogsResponse

from slack_sdk.audit_logs import AuditLogsClient, AuditLogsResponse
from tests.slack_sdk.audit_logs.mock_web_api_server import (
    cleanup_mock_web_api_server,
    setup_mock_web_api_server,
)


class TestAuditLogsClient(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_logs(self):
        json_data = """{
  "entries": [
    {
      "id": "xxx-yyy-zzz-111",
      "date_create": 1611221649,
      "action": "user_login",
      "new_attribute": "this should be just accepted as unknown attribute",
      "actor": {
        "type": "user",
        "new_attribute": "this should be just accepted as unknown attribute",
        "user": {
          "id": "W111",
          "name": "your name",
          "email": "foo@example.com",
          "team": "E111"
        }
      },
      "entity": {
        "type": "user",
        "new_attribute": "this should be just accepted as unknown attribute",
        "user": {
          "id": "W111",
          "name": "your name",
          "email": "foo@example.com",
          "team": "E111"
        }
      },
      "context": {
        "new_attribute": "this should be just accepted as unknown attribute",
        "location": {
          "type": "workspace",
          "id": "T111",
          "new_attribute": "this should be just accepted as unknown attribute",
          "name": "WS",
          "domain": "foo-bar-baz"
        },
        "ua": "UA",
        "ip_address": "1.2.3.4",
        "session_id": 1656410836837
      }
    },
    {
      "id": "32c68de4-cbfa-4fcb-9780-25fdd5aacf32",
      "date_create": 1611221649,
      "action": "user_login",
      "actor": {
        "type": "user",
        "user": {
          "id": "W111",
          "name": "your name",
          "email": "foo@example.com",
          "team": "E111"
        }
      },
      "entity": {
        "type": "user",
        "user": {
          "id": "W111",
          "name": "your name",
          "email": "foo@example.com",
          "team": "E111"
        }
      },
      "context": {
        "location": {
          "type": "workspace",
          "id": "T111",
          "name": "WS",
          "domain": "foo-bar-baz"
        },
        "ua": "UA",
        "ip_address": "1.2.3.4",
        "session_id": 1656410836837
      }
    }
  ],
  "response_metadata": {
    "next_cursor": "xxx",
    "new_attribute": "this should be just accepted as unknown attribute"
  },
  "new_attribute": "this should be just accepted as unknown attribute"
}
"""
        logs = LogsResponse(**json.loads(json_data))
        self.assertIsNotNone(logs)
        self.assertIsNotNone(logs.entries[0].unknown_fields.get("new_attribute"))
        self.assertIsNotNone(logs.response_metadata.unknown_fields.get("new_attribute"))
        self.assertIsNotNone(logs.unknown_fields.get("new_attribute"))
