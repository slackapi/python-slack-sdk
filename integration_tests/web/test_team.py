import os
import unittest

from integration_tests.env_variable_names import SLACK_SDK_TEST_BOT_TOKEN
from slack_sdk.web import WebClient


class TestWebClient(unittest.TestCase):
    def setUp(self):
        self.bot_token = os.environ[SLACK_SDK_TEST_BOT_TOKEN]
        self.client: WebClient = WebClient(token=self.bot_token)

    def tearDown(self):
        pass

    def test_team_billing_info(self):
        response = self.client.team_billing_info()
        self.assertIsNone(response.get("error"))
        self.assertIsNotNone(response.get("plan"))

    def test_team_preferences_list(self):
        response = self.client.team_preferences_list()
        self.assertIsNone(response.get("error"))
        self.assertIsNotNone(response.get("msg_edit_window_mins"))
        self.assertIsNotNone(response.get("allow_message_deletion"))
        self.assertIsNotNone(response.get("display_real_names"))
        self.assertIsNotNone(response.get("disable_file_uploads"))
        self.assertIsNotNone(response.get("who_can_post_general"))
