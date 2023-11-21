import os
import unittest

from slack_sdk.web import WebClient


class TestWebClient(unittest.TestCase):
    """Runs integration tests with real Slack API"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_operations(self):
        token = os.environ["SLACK_SDK_TEST_TOOLING_TOKEN"]  # xoxe.xoxp-...
        client = WebClient(token)
        client.apps_manifest_validate(manifest=STR_MANIFEST)
        client.apps_manifest_validate(manifest=DICT_MANIFEST)

        response = client.apps_manifest_create(manifest=STR_MANIFEST)
        app_id = response["app_id"]
        try:
            client.apps_manifest_update(app_id=app_id, manifest=DICT_MANIFEST)
            client.apps_manifest_export(app_id=app_id)
        finally:
            client.apps_manifest_delete(app_id=app_id)


STR_MANIFEST = """{
    "display_information": {
        "name": "manifest-sandbox"
    },
    "features": {
        "app_home": {
            "home_tab_enabled": true,
            "messages_tab_enabled": false,
            "messages_tab_read_only_enabled": false
        },
        "bot_user": {
            "display_name": "manifest-sandbox",
            "always_online": true
        },
        "shortcuts": [
            {
                "name": "message one",
                "type": "message",
                "callback_id": "m",
                "description": "message"
            },
            {
                "name": "global one",
                "type": "global",
                "callback_id": "g",
                "description": "global"
            }
        ],
        "slash_commands": [
            {
                "command": "/hey",
                "url": "https://www.example.com/",
                "description": "What's up?",
                "usage_hint": "What's up?",
                "should_escape": true
            }
        ],
        "unfurl_domains": [
            "example.com"
        ]
    },
    "oauth_config": {
        "redirect_urls": [
            "https://www.example.com/foo"
        ],
        "scopes": {
            "user": [
                "search:read",
                "channels:read",
                "groups:read",
                "mpim:read"
            ],
            "bot": [
                "commands",
                "incoming-webhook",
                "app_mentions:read",
                "links:read"
            ]
        }
    },
    "settings": {
        "allowed_ip_address_ranges": [
            "123.123.123.123/32"
        ],
        "event_subscriptions": {
            "request_url": "https://www.example.com/slack/events",
            "user_events": [
                "member_joined_channel"
            ],
            "bot_events": [
                "app_mention",
                "link_shared"
            ]
        },
        "interactivity": {
            "is_enabled": true,
            "request_url": "https://www.example.com/",
            "message_menu_options_url": "https://www.example.com/"
        },
        "org_deploy_enabled": true,
        "socket_mode_enabled": false,
        "token_rotation_enabled": true
    }
}
"""

DICT_MANIFEST = {
    "display_information": {"name": "manifest-sandbox"},
    "features": {
        "app_home": {"home_tab_enabled": True, "messages_tab_enabled": False, "messages_tab_read_only_enabled": False},
        "bot_user": {"display_name": "manifest-sandbox", "always_online": True},
        "shortcuts": [
            {"name": "message one", "type": "message", "callback_id": "m", "description": "message"},
            {"name": "global one", "type": "global", "callback_id": "g", "description": "global"},
        ],
        "slash_commands": [
            {
                "command": "/hey",
                "url": "https://www.example.com/",
                "description": "What's up?",
                "usage_hint": "What's up?",
                "should_escape": True,
            }
        ],
        "unfurl_domains": ["example.com"],
    },
    "oauth_config": {
        "redirect_urls": ["https://www.example.com/foo"],
        "scopes": {
            "user": ["search:read", "channels:read", "groups:read", "mpim:read"],
            "bot": ["commands", "incoming-webhook", "app_mentions:read", "links:read"],
        },
    },
    "settings": {
        "allowed_ip_address_ranges": ["123.123.123.123/32"],
        "event_subscriptions": {
            "request_url": "https://www.example.com/slack/events",
            "user_events": ["member_joined_channel"],
            "bot_events": ["app_mention", "link_shared"],
        },
        "interactivity": {
            "is_enabled": True,
            "request_url": "https://www.example.com/",
            "message_menu_options_url": "https://www.example.com/",
        },
        "org_deploy_enabled": True,
        "socket_mode_enabled": False,
        "token_rotation_enabled": True,
    },
}
