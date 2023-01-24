import json
import unittest

from slack_sdk.audit_logs.v1.logs import LogsResponse


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

    def test_logs_complete(self):
        logs = LogsResponse(**json.loads(logs_response_data))
        self.assertIsNotNone(logs)
        self.assertEqual(logs.response_metadata.next_cursor, "")
        entry = logs.entries[0]
        self.assertEqual(
            list(entry.details.unknown_fields.keys()),
            [],
            f"found: {entry.details.unknown_fields.keys()}",
        )
        self.assertEqual(
            list(entry.entity.unknown_fields.keys()),
            [],
            f"found: {entry.entity.unknown_fields.keys()}",
        )
        self.assertEqual(
            list(entry.context.unknown_fields.keys()),
            [],
            f"found: {entry.context.unknown_fields.keys()}",
        )
        self.assertEqual(
            list(entry.actor.unknown_fields.keys()),
            [],
            f"found: {entry.actor.unknown_fields.keys()}",
        )
        self.assertEqual(entry.details.is_token_rotation_enabled_app, True)
        self.assertEqual(entry.details.inviter.id, "inviter_id")
        self.assertEqual(entry.details.kicker.id, "kicker_id")
        self.assertEqual(entry.details.old_retention_policy.type, "old")
        self.assertEqual(entry.details.new_retention_policy.type, "new")
        self.assertEqual(entry.details.is_internal_integration, True)
        self.assertEqual(entry.details.cleared_resolution, "approved")
        self.assertEqual(entry.details.who_can_post.type, ["owner", "admin"])
        self.assertEqual(entry.details.who_can_post.user, ["W111"])
        self.assertEqual(entry.details.can_thread.type, ["admin", "org_admin"])
        self.assertEqual(entry.details.can_thread.user, ["W222"])
        self.assertEqual(entry.details.is_external_limited, True)
        # Due to historical reasons, succeeded_users/failed_users can be
        # either an array or a single string with encoded JSON data
        self.assertEqual(entry.details.succeeded_users, ["W111", "W222"])
        self.assertEqual(entry.details.failed_users, ["W333", "W444"])
        self.assertEqual(entry.details.exporting_team_id, 1134128598372)


logs_response_data = """{
  "ok": false,
  "warning": "",
  "error": "",
  "needed": "",
  "provided": "",
  "response_metadata": {
    "next_cursor": ""
  },
  "entries": [
    {
      "id": "",
      "date_create": 123,
      "action": "",
      "actor": {
        "type": "",
        "user": {
          "id": "",
          "name": "",
          "email": "",
          "team": ""
        }
      },
      "entity": {
        "type": "",
        "app": {
          "id": "",
          "name": "",
          "is_distributed": false,
          "is_directory_approved": false,
          "is_workflow_app": false,
          "scopes": [
            ""
          ]
        },
        "user": {
          "id": "",
          "name": "",
          "email": "",
          "team": ""
        },
        "usergroup": {
          "id": "",
          "name": ""
        },
        "workspace": {
          "id": "",
          "name": "",
          "domain": ""
        },
        "enterprise": {
          "id": "",
          "name": "",
          "domain": ""
        },
        "file": {
          "id": "",
          "name": "",
          "filetype": "",
          "title": ""
        },
        "channel": {
          "id": "",
          "name": "",
          "privacy": "",
          "is_shared": false,
          "is_org_shared": false,
          "teams_shared_with": [
            ""
          ],
          "original_connected_channel_id": ""
        },
        "workflow": {
          "id": "",
          "name": ""
        },
        "barrier": {
          "id": "",
          "primary_usergroup": "",
          "barriered_from_usergroups": [
            ""
          ],
          "restricted_subjects": [
            ""
          ]
        }
      },
      "context": {
        "session_id": "",
        "location": {
          "type": "",
          "id": "",
          "name": "",
          "domain": ""
        },
        "ua": "",
        "ip_address": ""
      },
      "details": {
        "type": "",
        "app_owner_id": "",
        "scopes": [
          ""
        ],
        "bot_scopes": [
          ""
        ],
        "new_scopes": [
          ""
        ],
        "previous_scopes": [
          ""
        ],
        "inviter": {
          "id": "inviter_id",
          "name": "",
          "email": "",
          "team": ""
        },
        "kicker": {
          "id": "kicker_id",
          "name": "",
          "email": "",
          "team": ""
        },
        "installer_user_id": "",
        "approver_id": "",
        "approval_type": "",
        "app_previously_approved": false,
        "old_scopes": [
          ""
        ],
        "name": "",
        "bot_id": "",
        "channels": [
          ""
        ],
        "permissions": [
          {
            "resource": {
              "type": "",
              "grant": {
                "type": "",
                "resource_id": "",
                "wildcard": {
                  "type": ""
                }
              }
            },
            "scopes": [
              ""
            ]
          }
        ],
        "shared_to": "",
        "reason": "",
        "is_internal_integration": false,
        "is_workflow": false,
        "mobile_only": false,
        "web_only": false,
        "non_sso_only": false,
        "expires_on": 123,
        "new_version_id": "",
        "trigger": "",
        "granular_bot_token": false,
        "origin_team": "",
        "target_team": "",
        "resolution": "",
        "app_previously_resolved": false,
        "admin_app_id": "",
        "export_type": "",
        "export_start_ts": "",
        "export_end_ts": "",
        "barrier_id": "",
        "primary_usergroup_id": "",
        "barriered_from_usergroup_ids": [
          ""
        ],
        "restricted_subjects": [
          ""
        ],
        "duration": 123,
        "desktop_app_browser_quit": false,
        "invite_id": "",
        "external_organization_id": "",
        "external_organization_name": "",
        "external_user_id": "",
        "external_user_email": "",
        "channel_id": "",
        "added_team_id": "",
        "is_token_rotation_enabled_app": true,
        "old_retention_policy": {
          "type": "old",
          "duration_days": 111
        },
        "new_retention_policy": {
          "type": "new",
          "duration_days": 222
        },
        "is_internal_integration": true,
        "cleared_resolution": "approved",
        "who_can_post": {
          "type": [
            "owner",
            "admin"
          ],
          "user": [
            "W111"
          ]
        },
        "can_thread": {
          "type": [
            "admin",
            "org_admin"
          ],
          "user": [
            "W222"
          ]
        },
        "is_external_limited": true,
        "succeeded_users": "[\\\"W111\\\", \\\"W222\\\"]",
        "failed_users": "[\\\"W333\\\", \\\"W444\\\"]",
        "exporting_team_id": 1134128598372
      }
    }
  ]
}
"""
