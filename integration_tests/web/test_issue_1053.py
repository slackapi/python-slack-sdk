import logging
import os
import time
import unittest

from integration_tests.env_variable_names import SLACK_SDK_TEST_BOT_TOKEN
from slack_sdk.web import WebClient


class TestWebClient(unittest.TestCase):
    """Runs integration tests with real Slack API

    https://github.com/slackapi/python-slack-sdk/issues/1053
    """

    def setUp(self):
        self.logger = logging.getLogger(__name__)
        self.bot_token = os.environ[SLACK_SDK_TEST_BOT_TOKEN]

    def tearDown(self):
        pass

    def test_issue_1053(self):
        client: WebClient = WebClient(token=self.bot_token)
        self_user_id = client.auth_test()["user_id"]
        channel_name = f"test-channel-{str(time.time()).replace('.', '-')}"
        channel_id = None
        try:
            creation = client.conversations_create(name=channel_name)
            self.assertIsNone(creation.get("error"))
            channel_id = creation["channel"]["id"]
            user_ids = [
                u["id"]
                for u in client.users_list(limit=100)["members"]
                if u["id"] not in {"USLACKBOT", self_user_id}
                and u.get("is_bot", False) is False
                and u.get("is_app_user", False) is False
                and u.get("is_restricted", False) is False
                and u.get("is_ultra_restricted", False) is False
                and u.get("is_email_confirmed", False) is True
            ]
            invitations = client.conversations_invite(channel=channel_id, users=user_ids)
            self.assertIsNone(invitations.get("error"))
        finally:
            if channel_id is not None:
                client.conversations_archive(channel=channel_id)
