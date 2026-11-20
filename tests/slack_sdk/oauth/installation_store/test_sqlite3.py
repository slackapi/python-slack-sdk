import unittest

from slack_sdk.oauth.installation_store import Installation
from slack_sdk.oauth.installation_store.sqlite3 import SQLite3InstallationStore
from tests.helpers import async_test


class TestSQLite3(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_instance(self):
        store = SQLite3InstallationStore(database="logs/test.db", client_id="111.222")
        self.assertIsNotNone(store)
        conn = store.connect()
        self.assertIsNotNone(conn)
        conn.close()

    def test_init(self):
        store = SQLite3InstallationStore(database="logs/test.db", client_id="111.222")
        store.init()

    def test_save_and_find(self):
        store = SQLite3InstallationStore(database="logs/test.db", client_id="111.222")
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

        # find bots
        bot = store.find_bot(enterprise_id="E111", team_id="T111")
        self.assertIsNotNone(bot)
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

    def test_org_installation(self):
        store = SQLite3InstallationStore(database="logs/test.db", client_id="111.222")
        installation = Installation(
            app_id="AO111",
            enterprise_id="EO111",
            user_id="UO111",
            bot_id="BO111",
            bot_token="xoxb-O111",
            bot_scopes=["chat:write"],
            bot_user_id="UO222",
            is_enterprise_install=True,
        )
        store.save(installation)

        # find bots
        bot = store.find_bot(enterprise_id="EO111", team_id=None)
        self.assertIsNotNone(bot)
        bot = store.find_bot(enterprise_id="EO111", team_id="TO222", is_enterprise_install=True)
        self.assertIsNotNone(bot)
        bot = store.find_bot(enterprise_id="EO111", team_id="TO222")
        self.assertIsNone(bot)
        bot = store.find_bot(enterprise_id=None, team_id="TO111")
        self.assertIsNone(bot)

        # delete bots
        store.delete_bot(enterprise_id="EO111", team_id="TO222")
        bot = store.find_bot(enterprise_id="EO111", team_id=None)
        self.assertIsNotNone(bot)

        store.delete_bot(enterprise_id="EO111", team_id=None)
        bot = store.find_bot(enterprise_id="EO111", team_id=None)
        self.assertIsNone(bot)

        # find installations
        i = store.find_installation(enterprise_id="EO111", team_id=None)
        self.assertIsNotNone(i)
        i = store.find_installation(enterprise_id="EO111", team_id="T111", is_enterprise_install=True)
        self.assertIsNotNone(i)
        i = store.find_installation(enterprise_id="EO111", team_id="T222")
        self.assertIsNone(i)
        i = store.find_installation(enterprise_id=None, team_id="T111")
        self.assertIsNone(i)

        i = store.find_installation(enterprise_id="EO111", team_id=None, user_id="UO111")
        self.assertIsNotNone(i)
        i = store.find_installation(
            enterprise_id="E111",
            team_id="T111",
            is_enterprise_install=True,
            user_id="U222",
        )
        self.assertIsNone(i)
        i = store.find_installation(enterprise_id=None, team_id="T222", user_id="U111")
        self.assertIsNone(i)

        # delete installations
        store.delete_installation(enterprise_id="EO111", team_id=None, user_id="UO111")
        i = store.find_installation(enterprise_id="EO111", team_id=None, user_id="UO111")
        self.assertIsNone(i)

        store.save(installation)
        store.delete_installation(enterprise_id="EO111", team_id=None)
        i = store.find_installation(enterprise_id="EO111", team_id=None)
        self.assertIsNone(i)

        # delete all
        store.save(installation)
        store.delete_all(enterprise_id="EO111", team_id=None)

        i = store.find_installation(enterprise_id="EO111", team_id=None)
        self.assertIsNone(i)
        i = store.find_installation(enterprise_id="EO111", team_id=None, user_id="UO111")
        self.assertIsNone(i)
        bot = store.find_bot(enterprise_id="EO111", team_id=None)
        self.assertIsNone(bot)

    @async_test
    async def test_async_delete(self):
        store = SQLite3InstallationStore(database="logs/test.db", client_id="111.222")
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

        # delete installations
        await store.async_delete_installation(enterprise_id="E111", team_id="T111", user_id="U111")
        i = await store.async_find_installation(enterprise_id="E111", team_id="T111", user_id="U111")
        self.assertIsNone(i)

        # delete bots
        await store.async_delete_bot(enterprise_id="E111", team_id="T111")
        bot = await store.async_find_bot(enterprise_id="E111", team_id="T111")
        self.assertIsNone(bot)

        # delete all
        await store.async_save(installation)
        await store.async_delete_all(enterprise_id="E111", team_id="T111")

        i = await store.async_find_installation(enterprise_id="E111", team_id="T111")
        self.assertIsNone(i)
        bot = await store.async_find_bot(enterprise_id="E111", team_id="T111")
        self.assertIsNone(bot)

    def test_save_and_find_token_rotation(self):
        store = SQLite3InstallationStore(database="logs/test.db", client_id="111.222")

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

    def test_issue_1441_mixing_user_and_bot_installations(self):
        store = SQLite3InstallationStore(database="logs/test.db", client_id="111.222")

        bot_installation = Installation(
            app_id="A111",
            enterprise_id="E111",
            team_id="T111",
            user_id="U111",
            bot_id="B111",
            bot_token="xoxb-111",
            bot_scopes=["chat:write"],
            bot_user_id="U222",
        )
        store.save(bot_installation)

        # find bots
        bot = store.find_bot(enterprise_id="E111", team_id="T111")
        self.assertIsNotNone(bot)
        bot = store.find_bot(enterprise_id="E111", team_id="T222")
        self.assertIsNone(bot)
        bot = store.find_bot(enterprise_id=None, team_id="T111")
        self.assertIsNone(bot)

        installation = store.find_installation(enterprise_id="E111", team_id="T111")
        self.assertIsNotNone(installation.bot_token)
        installation = store.find_installation(enterprise_id="E111", team_id="T222")
        self.assertIsNone(installation)
        installation = store.find_installation(enterprise_id=None, team_id="T111")
        self.assertIsNone(installation)

        user_installation = Installation(
            app_id="A111",
            enterprise_id="E111",
            team_id="T111",
            user_id="U111",
            bot_scopes=["openid"],
            user_token="xoxp-111",
        )
        store.save(user_installation)

        # find bots
        bot = store.find_bot(enterprise_id="E111", team_id="T111")
        self.assertIsNotNone(bot.bot_token)
        bot = store.find_bot(enterprise_id="E111", team_id="T222")
        self.assertIsNone(bot)
        bot = store.find_bot(enterprise_id=None, team_id="T111")
        self.assertIsNone(bot)

        installation = store.find_installation(enterprise_id="E111", team_id="T111")
        self.assertIsNotNone(installation.bot_token)
        installation = store.find_installation(enterprise_id="E111", team_id="T222")
        self.assertIsNone(installation)
        installation = store.find_installation(enterprise_id=None, team_id="T111")
        self.assertIsNone(installation)

    def test_find_returns_latest_save_within_the_same_second(self):
        store = SQLite3InstallationStore(database="logs/test.db", client_id="111.222")
        store.delete_all(enterprise_id="E333", team_id="T333")

        for suffix in ["old", "new"]:
            store.save(
                Installation(
                    app_id="A333",
                    enterprise_id="E333",
                    team_id="T333",
                    user_id="U333",
                    bot_id="B333",
                    bot_token=f"xoxb-{suffix}",
                    bot_scopes=["chat:write"],
                    bot_user_id="U444",
                    user_token=f"xoxp-{suffix}",
                )
            )
        store.save(
            Installation(
                app_id="A333",
                enterprise_id="E333",
                team_id="T333",
                user_id="U555",
                user_token="xoxp-user-only",
            )
        )
        with store.connect() as conn:
            for table in ["slack_installations", "slack_bots"]:
                conn.execute(f"update {table} set installed_at = '2026-11-19 10:00:00' where enterprise_id = 'E333'")

        bot = store.find_bot(enterprise_id="E333", team_id="T333")
        self.assertEqual(bot.bot_token, "xoxb-new")

        installation = store.find_installation(enterprise_id="E333", team_id="T333")
        self.assertEqual(installation.user_token, "xoxp-user-only")
        self.assertEqual(installation.bot_token, "xoxb-new")

        installation = store.find_installation(enterprise_id="E333", team_id="T333", user_id="U333")
        self.assertEqual(installation.user_token, "xoxp-new")
        self.assertEqual(installation.bot_token, "xoxb-new")

        store.delete_all(enterprise_id="E333", team_id="T333")
