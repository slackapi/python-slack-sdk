import os
import unittest

from slack_sdk.oauth.installation_store import Installation
from slack_sdk.oauth.installation_store.cacheable_installation_store import (
    CacheableInstallationStore,
)
from slack_sdk.oauth.installation_store.sqlite3 import SQLite3InstallationStore


class TestCacheable(unittest.TestCase):
    def test_save_and_find(self):
        sqlite3_store = SQLite3InstallationStore(database="logs/cacheable.db", client_id="111.222")
        sqlite3_store.init()
        store = CacheableInstallationStore(sqlite3_store)

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
        store.save(installation)

        bot = store.find_bot(enterprise_id="E111", team_id="T111")
        self.assertIsNotNone(bot)

        os.remove("logs/cacheable.db")

        bot = sqlite3_store.find_bot(enterprise_id="E111", team_id="T111")
        self.assertIsNone(bot)
        bot = store.find_bot(enterprise_id="E111", team_id="T111")
        self.assertIsNotNone(bot)

        # delete and find
        sqlite3_store = SQLite3InstallationStore(database="logs/cacheable.db", client_id="111.222")
        sqlite3_store.init()
        store = CacheableInstallationStore(sqlite3_store)

        store.save(installation)
        bot = store.find_bot(enterprise_id="E111", team_id="T111")
        self.assertIsNotNone(bot)

        os.remove("logs/cacheable.db")
        bot = sqlite3_store.find_bot(enterprise_id="E111", team_id="T111")
        self.assertIsNone(bot)
        bot = store.find_bot(enterprise_id="E111", team_id="T111")
        self.assertIsNotNone(bot)

    def test_save_and_find_token_rotation(self):
        sqlite3_store = SQLite3InstallationStore(database="logs/cacheable.db", client_id="111.222")
        sqlite3_store.init()
        store = CacheableInstallationStore(sqlite3_store)

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
        store.save(installation)

        bot = store.find_bot(enterprise_id="E111", team_id="T111")
        self.assertIsNotNone(bot)
        self.assertEqual(bot.bot_refresh_token, "xoxe-1-initial")

        # Update the existing data
        refreshed_installation = Installation(
            app_id="A111",
            enterprise_id="E111",
            team_id="T111",
            user_id="U111",
            bot_id="B111",
            bot_token="xoxe.xoxp-1-refreshed",
            bot_scopes=["chat:write"],
            bot_user_id="U222",
            bot_refresh_token="xoxe-1-refreshed",
            bot_token_expires_in=43200,
        )
        store.save(refreshed_installation)

        # find bots
        bot = store.find_bot(enterprise_id="E111", team_id="T111")
        self.assertIsNotNone(bot)
        self.assertEqual(bot.bot_refresh_token, "xoxe-1-refreshed")
        bot = store.find_bot(enterprise_id="E111", team_id="T222")
        self.assertIsNone(bot)
        bot = store.find_bot(enterprise_id=None, team_id="T111")
        self.assertIsNone(bot)

        # delete bots
        store.delete_bot(enterprise_id="E111", team_id="T222")
        bot = store.find_bot(enterprise_id="E111", team_id="T222")
        self.assertIsNone(bot)

        # find installations
        i = store.find_installation(enterprise_id="E111", team_id="T111")
        self.assertIsNotNone(i)
        i = store.find_installation(enterprise_id="E111", team_id="T222")
        self.assertIsNone(i)
        i = store.find_installation(enterprise_id=None, team_id="T111")
        self.assertIsNone(i)

        i = store.find_installation(enterprise_id="E111", team_id="T111", user_id="U111")
        self.assertIsNotNone(i)
        i = store.find_installation(enterprise_id="E111", team_id="T111", user_id="U222")
        self.assertIsNone(i)
        i = store.find_installation(enterprise_id="E111", team_id="T222", user_id="U111")
        self.assertIsNone(i)

        # delete installations
        store.delete_installation(enterprise_id="E111", team_id="T111", user_id="U111")
        i = store.find_installation(enterprise_id="E111", team_id="T111", user_id="U111")
        self.assertIsNone(i)
        i = store.find_installation(enterprise_id="E111", team_id="T111")
        self.assertIsNone(i)

        # delete all
        store.save(installation)
        store.delete_all(enterprise_id="E111", team_id="T111")

        i = store.find_installation(enterprise_id="E111", team_id="T111")
        self.assertIsNone(i)
        i = store.find_installation(enterprise_id="E111", team_id="T111", user_id="U111")
        self.assertIsNone(i)
        bot = store.find_bot(enterprise_id="E111", team_id="T222")
        self.assertIsNone(bot)
