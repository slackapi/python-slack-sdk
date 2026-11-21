import unittest

from slack_sdk.audit_logs import AuditLogsClient
from slack_sdk.audit_logs.v1.async_client import AsyncAuditLogsClient
from slack_sdk.scim import SCIMClient
from slack_sdk.scim.v1.async_client import AsyncSCIMClient
from slack_sdk.web import WebClient
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.web.legacy_client import LegacyWebClient
from slack_sdk.webhook import WebhookClient
from slack_sdk.webhook.async_client import AsyncWebhookClient


class TestClientHeadersCopy(unittest.TestCase):
    """The headers dict given to a client constructor must not be shared with, or changed by, the client."""

    def _clients(self, headers: dict, user_agent_prefix: str) -> dict:
        return {
            "WebClient": WebClient(token="xoxb-valid", headers=headers, user_agent_prefix=user_agent_prefix),
            "AsyncWebClient": AsyncWebClient(token="xoxb-valid", headers=headers, user_agent_prefix=user_agent_prefix),
            "LegacyWebClient": LegacyWebClient(token="xoxb-valid", headers=headers, user_agent_prefix=user_agent_prefix),
            "WebhookClient": WebhookClient(
                "https://hooks.slack.com/services/T111/B111/xxx",
                default_headers=headers,
                user_agent_prefix=user_agent_prefix,
            ),
            "AsyncWebhookClient": AsyncWebhookClient(
                "https://hooks.slack.com/services/T111/B111/xxx",
                default_headers=headers,
                user_agent_prefix=user_agent_prefix,
            ),
            "AuditLogsClient": AuditLogsClient(
                token="xoxp-valid", default_headers=headers, user_agent_prefix=user_agent_prefix
            ),
            "AsyncAuditLogsClient": AsyncAuditLogsClient(
                token="xoxp-valid", default_headers=headers, user_agent_prefix=user_agent_prefix
            ),
            "SCIMClient": SCIMClient(token="xoxp-valid", default_headers=headers, user_agent_prefix=user_agent_prefix),
            "AsyncSCIMClient": AsyncSCIMClient(
                token="xoxp-valid", default_headers=headers, user_agent_prefix=user_agent_prefix
            ),
        }

    @staticmethod
    def _sent_headers(client) -> dict:
        return client.default_headers if hasattr(client, "default_headers") else client.headers

    def test_caller_headers_are_not_modified(self):
        headers = {"X-Trace": "1"}
        for name, client in self._clients(headers, "app-a").items():
            with self.subTest(client=name):
                self.assertEqual(headers, {"X-Trace": "1"})
                self.assertEqual(self._sent_headers(client)["X-Trace"], "1")
                self.assertTrue(self._sent_headers(client)["User-Agent"].startswith("app-a "))

    def test_clients_built_from_the_same_headers_keep_their_own_user_agent(self):
        headers = {"X-Trace": "1"}
        first = self._clients(headers, "app-a")
        second = self._clients(headers, "app-b")
        for name in first:
            with self.subTest(client=name):
                self.assertTrue(self._sent_headers(first[name])["User-Agent"].startswith("app-a "))
                self.assertTrue(self._sent_headers(second[name])["User-Agent"].startswith("app-b "))
