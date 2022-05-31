import os
import unittest

from slack_sdk.oauth.installation_store import Installation
from slack_sdk.oauth.installation_store.async_cacheable_installation_store import (
    AsyncCacheableInstallationStore,
)
from slack_sdk.oauth.installation_store.sqlite3 import SQLite3InstallationStore
from tests.helpers import async_test


class TestCacheable(unittest.TestCase):
    @async_test
    async def test_save_and_find(self):
        sqlite3_store = SQLite3InstallationStore(database="logs/cacheable.db", client_id="111.222")
        sqlite3_store.init()
        store = AsyncCacheableInstallationStore(sqlite3_store)

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
        await store.async_save(installation)

        bot = await store.async_find_bot(enterprise_id="E111", team_id="T111")
        self.assertIsNotNone(bot)

        os.remove("logs/cacheable.db")

        bot = await sqlite3_store.async_find_bot(enterprise_id="E111", team_id="T111")
        self.assertIsNone(bot)
        bot = await store.async_find_bot(enterprise_id="E111", team_id="T111")
        self.assertIsNotNone(bot)

    @async_test
    async def test_save_and_find_token_rotation(self):
        sqlite3_store = SQLite3InstallationStore(database="logs/cacheable.db", client_id="111.222")
        sqlite3_store.init()
        store = AsyncCacheableInstallationStore(sqlite3_store)

        installation = Installation(
            app_id="A111",
            enterprise_id="E111",
            team_id="T111",
            user_id="U111",
            bot_id="B111",
            bot_token="xoxb-initial",
            bot_scopes=["chat:write"],
            bot_user_id="U222",
            bot_refresh_token="xoxe-1-initial",
            bot_token_expires_in=43200,
        )
        await store.async_save(installation)

        bot = await store.async_find_bot(enterprise_id="E111", team_id="T111")
        self.assertIsNotNone(bot)
        self.assertEqual(bot.bot_refresh_token, "xoxe-1-initial")

        installation = Installation(
            app_id="A111",
            enterprise_id="E111",
            team_id="T111",
            user_id="U111",
            bot_id="B111",
            bot_token="xoxb-refreshed",
            bot_scopes=["chat:write"],
            bot_user_id="U222",
            bot_refresh_token="xoxe-1-refreshed",
            bot_token_expires_in=43200,
        )
        await store.async_save(installation)

        bot = await store.async_find_bot(enterprise_id="E111", team_id="T111")
        self.assertIsNotNone(bot)
        self.assertEqual(bot.bot_refresh_token, "xoxe-1-refreshed")

        os.remove("logs/cacheable.db")

        bot = await sqlite3_store.async_find_bot(enterprise_id="E111", team_id="T111")
        self.assertIsNone(bot)
        bot = await store.async_find_bot(enterprise_id="E111", team_id="T111")
        self.assertIsNotNone(bot)
