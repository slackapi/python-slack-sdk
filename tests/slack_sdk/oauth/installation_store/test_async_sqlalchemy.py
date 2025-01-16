import unittest
from tests.helpers import async_test
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from slack_sdk.oauth.installation_store import Installation
from slack_sdk.oauth.installation_store.sqlalchemy import AsyncSQLAlchemyInstallationStore


class TestAsyncSQLAlchemy(unittest.TestCase):
    engine: AsyncEngine

    @async_test
    async def setUp(self):
        self.engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        self.store = AsyncSQLAlchemyInstallationStore(client_id="111.222", engine=self.engine)
        async with self.engine.begin() as conn:
            await conn.run_sync(self.store.metadata.create_all)

    @async_test
    async def tearDown(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(self.store.metadata.drop_all)
        await self.engine.dispose()

    @async_test
    async def test_save_and_find(self):
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
        await self.store.async_save(installation)

        store = self.store

        # find bots
        bot = await store.async_find_bot(enterprise_id="E111", team_id="T111")
        self.assertIsNotNone(bot)
        bot = await store.async_find_bot(enterprise_id="E111", team_id="T222")
        self.assertIsNone(bot)
        bot = await store.async_find_bot(enterprise_id=None, team_id="T111")
        self.assertIsNone(bot)

        # delete bots
        await store.async_delete_bot(enterprise_id="E111", team_id="T222")
        bot = await store.async_find_bot(enterprise_id="E111", team_id="T222")
        self.assertIsNone(bot)

        # find installations
        i = await store.async_find_installation(enterprise_id="E111", team_id="T111")
        self.assertIsNotNone(i)
        i = await store.async_find_installation(enterprise_id="E111", team_id="T222")
        self.assertIsNone(i)
        i = await store.async_find_installation(enterprise_id=None, team_id="T111")
        self.assertIsNone(i)

        i = await store.async_find_installation(enterprise_id="E111", team_id="T111", user_id="U111")
        self.assertIsNotNone(i)
        i = await store.async_find_installation(enterprise_id="E111", team_id="T111", user_id="U222")
        self.assertIsNone(i)
        i = await store.async_find_installation(enterprise_id="E111", team_id="T222", user_id="U111")
        self.assertIsNone(i)

        # delete installations
        await store.async_delete_installation(enterprise_id="E111", team_id="T111", user_id="U111")
        i = await store.async_find_installation(enterprise_id="E111", team_id="T111", user_id="U111")
        self.assertIsNone(i)
        i = await store.async_find_installation(enterprise_id="E111", team_id="T111")
        self.assertIsNone(i)

        # delete all
        await store.async_save(installation)
        await store.async_delete_all(enterprise_id="E111", team_id="T111")

        i = await store.async_find_installation(enterprise_id="E111", team_id="T111")
        self.assertIsNone(i)
        i = await store.async_find_installation(enterprise_id="E111", team_id="T111", user_id="U111")
        self.assertIsNone(i)
        bot = await store.async_find_bot(enterprise_id="E111", team_id="T222")
        self.assertIsNone(bot)

    @async_test
    async def test_org_installation(self):
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
        await self.store.async_save(installation)

        store = self.store

        # find bots
        bot = await store.async_find_bot(enterprise_id="EO111", team_id=None)
        self.assertIsNotNone(bot)
        bot = await store.async_find_bot(enterprise_id="EO111", team_id="TO222", is_enterprise_install=True)
        self.assertIsNotNone(bot)
        bot = await store.async_find_bot(enterprise_id="EO111", team_id="TO222")
        self.assertIsNone(bot)
        bot = await store.async_find_bot(enterprise_id=None, team_id="TO111")
        self.assertIsNone(bot)

        # delete bots
        await store.async_delete_bot(enterprise_id="EO111", team_id="TO222")
        bot = await store.async_find_bot(enterprise_id="EO111", team_id=None)
        self.assertIsNotNone(bot)

        await store.async_delete_bot(enterprise_id="EO111", team_id=None)
        bot = await store.async_find_bot(enterprise_id="EO111", team_id=None)
        self.assertIsNone(bot)

        # find installations
        i = await store.async_find_installation(enterprise_id="EO111", team_id=None)
        self.assertIsNotNone(i)
        i = await store.async_find_installation(enterprise_id="EO111", team_id="T111", is_enterprise_install=True)
        self.assertIsNotNone(i)
        i = await store.async_find_installation(enterprise_id="EO111", team_id="T222")
        self.assertIsNone(i)
        i = await store.async_find_installation(enterprise_id=None, team_id="T111")
        self.assertIsNone(i)

        i = await store.async_find_installation(enterprise_id="EO111", team_id=None, user_id="UO111")
        self.assertIsNotNone(i)
        i = await store.async_find_installation(
            enterprise_id="E111",
            team_id="T111",
            is_enterprise_install=True,
            user_id="U222",
        )
        self.assertIsNone(i)
        i = await store.async_find_installation(enterprise_id=None, team_id="T222", user_id="U111")
        self.assertIsNone(i)

        # delete installations
        await store.async_delete_installation(enterprise_id="E111", team_id=None)
        i = await store.async_find_installation(enterprise_id="E111", team_id=None)
        self.assertIsNone(i)

        # delete all
        await store.async_save(installation)
        await store.async_delete_all(enterprise_id="E111", team_id=None)

        i = await store.async_find_installation(enterprise_id="E111", team_id=None)
        self.assertIsNone(i)
        i = await store.async_find_installation(enterprise_id="E111", team_id=None, user_id="U111")
        self.assertIsNone(i)
        bot = await store.async_find_bot(enterprise_id=None, team_id="T222")
        self.assertIsNone(bot)

    @async_test
    async def test_save_and_find_token_rotation(self):
        store = self.store

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
        await store.async_save(installation)

        bot = await store.async_find_bot(enterprise_id="E111", team_id="T111")
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
        await store.async_save(refreshed_installation)

        # find bots
        bot = await store.async_find_bot(enterprise_id="E111", team_id="T111")
        self.assertIsNotNone(bot)
        self.assertEqual(bot.bot_refresh_token, "xoxe-1-refreshed")
        bot = await store.async_find_bot(enterprise_id="E111", team_id="T222")
        self.assertIsNone(bot)
        bot = await store.async_find_bot(enterprise_id=None, team_id="T111")
        self.assertIsNone(bot)

        # delete bots
        await store.async_delete_bot(enterprise_id="E111", team_id="T222")
        bot = await store.async_find_bot(enterprise_id="E111", team_id="T222")
        self.assertIsNone(bot)

        # find installations
        i = await store.async_find_installation(enterprise_id="E111", team_id="T111")
        self.assertIsNotNone(i)
        i = await store.async_find_installation(enterprise_id="E111", team_id="T222")
        self.assertIsNone(i)
        i = await store.async_find_installation(enterprise_id=None, team_id="T111")
        self.assertIsNone(i)

        i = await store.async_find_installation(enterprise_id="E111", team_id="T111", user_id="U111")
        self.assertIsNotNone(i)
        i = await store.async_find_installation(enterprise_id="E111", team_id="T111", user_id="U222")
        self.assertIsNone(i)
        i = await store.async_find_installation(enterprise_id="E111", team_id="T222", user_id="U111")
        self.assertIsNone(i)

        # delete installations
        await store.async_delete_installation(enterprise_id="E111", team_id="T111", user_id="U111")
        i = await store.async_find_installation(enterprise_id="E111", team_id="T111", user_id="U111")
        self.assertIsNone(i)
        i = await store.async_find_installation(enterprise_id="E111", team_id="T111")
        self.assertIsNone(i)

        # delete all
        await store.async_save(installation)
        await store.async_delete_all(enterprise_id="E111", team_id="T111")

        i = await store.async_find_installation(enterprise_id="E111", team_id="T111")
        self.assertIsNone(i)
        i = await store.async_find_installation(enterprise_id="E111", team_id="T111", user_id="U111")
        self.assertIsNone(i)
        bot = await store.async_find_bot(enterprise_id="E111", team_id="T222")
        self.assertIsNone(bot)

    @async_test
    async def test_issue_1441_mixing_user_and_bot_installations(self):
        store = self.store

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
        await store.async_save(bot_installation)

        # find bots
        bot = await store.async_find_bot(enterprise_id="E111", team_id="T111")
        self.assertIsNotNone(bot)
        bot = await store.async_find_bot(enterprise_id="E111", team_id="T222")
        self.assertIsNone(bot)
        bot = await store.async_find_bot(enterprise_id=None, team_id="T111")
        self.assertIsNone(bot)

        installation = await store.async_find_installation(enterprise_id="E111", team_id="T111")
        self.assertIsNotNone(installation.bot_token)
        installation = await store.async_find_installation(enterprise_id="E111", team_id="T222")
        self.assertIsNone(installation)
        installation = await store.async_find_installation(enterprise_id=None, team_id="T111")
        self.assertIsNone(installation)

        user_installation = Installation(
            app_id="A111",
            enterprise_id="E111",
            team_id="T111",
            user_id="U111",
            bot_scopes=["openid"],
            user_token="xoxp-111",
        )
        await store.async_save(user_installation)

        # find bots
        bot = await store.async_find_bot(enterprise_id="E111", team_id="T111")
        self.assertIsNotNone(bot.bot_token)
        bot = await store.async_find_bot(enterprise_id="E111", team_id="T222")
        self.assertIsNone(bot)
        bot = await store.async_find_bot(enterprise_id=None, team_id="T111")
        self.assertIsNone(bot)

        installation = await store.async_find_installation(enterprise_id="E111", team_id="T111")
        self.assertIsNotNone(installation.bot_token)
        installation = await store.async_find_installation(enterprise_id="E111", team_id="T222")
        self.assertIsNone(installation)
        installation = await store.async_find_installation(enterprise_id=None, team_id="T111")
        self.assertIsNone(installation)
