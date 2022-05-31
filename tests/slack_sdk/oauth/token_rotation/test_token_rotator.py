import unittest

from slack_sdk.errors import SlackTokenRotationError
from slack_sdk.oauth.installation_store import Installation
from slack_sdk.oauth.token_rotation import TokenRotator
from slack_sdk.web import WebClient
from tests.slack_sdk.web.mock_web_api_server import (
    setup_mock_web_api_server,
    cleanup_mock_web_api_server,
)


class TestTokenRotator(unittest.TestCase):
    def setUp(self):
        setup_mock_web_api_server(self)
        self.token_rotator = TokenRotator(
            client=WebClient(base_url="http://localhost:8888", token=None),
            client_id="111.222",
            client_secret="token_rotation_secret",
        )

    def tearDown(self):
        cleanup_mock_web_api_server(self)

    def test_refresh(self):
        installation = Installation(
            app_id="A111",
            enterprise_id="E111",
            team_id="T111",
            user_id="U111",
            bot_id="B111",
            bot_token="xoxe.xoxp-1-initial",
            bot_scopes=["chat:write"],
            bot_user_id="U222",
            bot_refresh_token="xoxe-1-initial",
            bot_token_expires_in=43200,
        )
        refreshed = self.token_rotator.perform_token_rotation(
            installation=installation, minutes_before_expiration=60 * 24 * 365
        )
        self.assertIsNotNone(refreshed)

        should_not_be_refreshed = self.token_rotator.perform_token_rotation(
            installation=installation, minutes_before_expiration=1
        )
        self.assertIsNone(should_not_be_refreshed)

    def test_token_rotation_disabled(self):
        installation = Installation(
            app_id="A111",
            enterprise_id="E111",
            team_id="T111",
            user_id="U111",
            bot_id="B111",
            bot_token="xoxe.xoxp-1-initial",
            bot_scopes=["chat:write"],
            bot_user_id="U222",
        )
        should_not_be_refreshed = self.token_rotator.perform_token_rotation(
            installation=installation, minutes_before_expiration=60 * 24 * 365
        )
        self.assertIsNone(should_not_be_refreshed)

        should_not_be_refreshed = self.token_rotator.perform_token_rotation(
            installation=installation, minutes_before_expiration=1
        )
        self.assertIsNone(should_not_be_refreshed)

    def test_refresh_error(self):
        token_rotator = TokenRotator(
            client=WebClient(base_url="http://localhost:8888", token=None),
            client_id="111.222",
            client_secret="invalid_value",
        )

        installation = Installation(
            app_id="A111",
            enterprise_id="E111",
            team_id="T111",
            user_id="U111",
            bot_id="B111",
            bot_token="xoxe.xoxp-1-initial",
            bot_scopes=["chat:write"],
            bot_user_id="U222",
            bot_refresh_token="xoxe-1-initial",
            bot_token_expires_in=43200,
        )
        with self.assertRaises(SlackTokenRotationError):
            token_rotator.perform_token_rotation(installation=installation, minutes_before_expiration=60 * 24 * 365)
