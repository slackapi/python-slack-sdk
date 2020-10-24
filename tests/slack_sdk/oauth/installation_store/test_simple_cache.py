import os
import unittest

from slack_sdk.oauth.installation_store import Installation
from slack_sdk.oauth.installation_store.cacheable_installation_store import CacheableInstallationStore
from slack_sdk.oauth.installation_store.sqlite3 import SQLite3InstallationStore


class TestCacheable(unittest.TestCase):

    def test_save_and_find(self):
        sqlite3_store = SQLite3InstallationStore(
            database="logs/cacheable.db",
            client_id="111.222"
        )
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
            bot_user_id="U222"
        )
        store.save(installation)

        bot = store.find_bot(enterprise_id="E111", team_id="T111")
        self.assertIsNotNone(bot)

        os.remove("logs/cacheable.db")

        bot = sqlite3_store.find_bot(enterprise_id="E111", team_id="T111")
        self.assertIsNone(bot)
        bot = store.find_bot(enterprise_id="E111", team_id="T111")
        self.assertIsNotNone(bot)
