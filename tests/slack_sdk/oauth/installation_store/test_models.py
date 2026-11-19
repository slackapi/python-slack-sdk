import time
from datetime import datetime, timezone
import unittest

from slack_sdk.oauth.installation_store import Installation, FileInstallationStore, Bot


class TestModels(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_bot(self):
        bot = Bot(
            bot_token="xoxb-",
            bot_id="B111",
            bot_user_id="U111",
            installed_at=time.time(),
        )
        self.assertIsNotNone(bot)
        self.assertIsNotNone(bot.to_dict())
        self.assertIsNotNone(bot.to_dict_for_copying())

    def test_bot_custom_fields(self):
        bot = Bot(
            bot_token="xoxb-",
            bot_id="B111",
            bot_user_id="U111",
            installed_at=time.time(),
        )
        bot.set_custom_value("service_user_id", "XYZ123")
        # the same names in custom_values are ignored
        bot.set_custom_value("app_id", "A222")
        self.assertEqual(bot.get_custom_value("service_user_id"), "XYZ123")
        self.assertEqual(bot.to_dict().get("service_user_id"), "XYZ123")
        self.assertEqual(bot.to_dict_for_copying().get("custom_values").get("service_user_id"), "XYZ123")

    def test_bot_datetime_manipulation(self):
        expected_timestamp = datetime.now(tz=timezone.utc)
        bot = Bot(
            bot_token="xoxb-",
            bot_id="B111",
            bot_user_id="U111",
            bot_token_expires_at=expected_timestamp,
            installed_at=expected_timestamp,
        )
        bot_dict = bot.to_dict()
        self.assertIsNotNone(bot_dict)
        self.assertEqual(
            bot_dict.get("bot_token_expires_at").isoformat(), expected_timestamp.strftime("%Y-%m-%dT%H:%M:%S+00:00")
        )
        self.assertEqual(bot_dict.get("installed_at"), expected_timestamp)

    def test_installation(self):
        installation = Installation(
            app_id="A111",
            enterprise_id="E111",
            team_id="T111",
            user_id="U111",
            bot_id="B111",
            bot_token="xoxb-111",
            bot_scopes=["chat:write"],
            bot_user_id="U222",
        )
        self.assertIsNotNone(installation)
        self.assertEqual(installation.app_id, "A111")

        self.assertIsNotNone(installation.to_bot())
        self.assertIsNotNone(installation.to_bot().app_id, "A111")

        self.assertIsNotNone(installation.to_dict())
        self.assertEqual(installation.to_dict().get("app_id"), "A111")

    def test_installation_custom_fields(self):
        installation = Installation(
            app_id="A111",
            enterprise_id="E111",
            team_id="T111",
            user_id="U111",
            bot_id="B111",
            bot_token="xoxb-111",
            bot_scopes=["chat:write"],
            bot_user_id="U222",
        )
        self.assertIsNotNone(installation)

        installation.set_custom_value("service_user_id", "XYZ123")
        # the same names in custom_values are ignored
        installation.set_custom_value("app_id", "A222")
        self.assertEqual(installation.get_custom_value("service_user_id"), "XYZ123")
        self.assertEqual(installation.to_dict().get("service_user_id"), "XYZ123")
        self.assertEqual(installation.to_dict().get("app_id"), "A111")
        self.assertEqual(installation.to_dict_for_copying().get("custom_values").get("app_id"), "A222")

        bot = installation.to_bot()
        self.assertEqual(bot.app_id, "A111")
        self.assertEqual(bot.get_custom_value("service_user_id"), "XYZ123")

        self.assertEqual(bot.to_dict().get("app_id"), "A111")
        self.assertEqual(bot.to_dict().get("service_user_id"), "XYZ123")
        self.assertEqual(bot.to_dict_for_copying().get("custom_values").get("app_id"), "A222")

    def test_installation_datetime_manipulation(self):
        expected_timestamp = datetime.now(tz=timezone.utc)
        installation = Installation(
            app_id="A111",
            enterprise_id="E111",
            team_id="T111",
            user_id="U111",
            bot_id="B111",
            bot_token="xoxb-111",
            bot_scopes=["chat:write"],
            bot_user_id="U222",
            bot_token_expires_at=expected_timestamp,
            user_token_expires_at=expected_timestamp,
            installed_at=expected_timestamp,
        )
        installation_dict = installation.to_dict()
        self.assertIsNotNone(installation_dict)
        self.assertEqual(
            installation_dict.get("bot_token_expires_at").isoformat(), expected_timestamp.strftime("%Y-%m-%dT%H:%M:%S+00:00")
        )
        self.assertEqual(
            installation_dict.get("user_token_expires_at").isoformat(),
            expected_timestamp.strftime("%Y-%m-%dT%H:%M:%S+00:00"),
        )
        self.assertEqual(installation_dict.get("installed_at"), expected_timestamp)
