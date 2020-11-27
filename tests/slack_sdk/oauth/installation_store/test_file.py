import unittest

from slack_sdk.oauth.installation_store import Installation, FileInstallationStore


class TestFile(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_instance(self):
        store = FileInstallationStore(client_id="111.222")
        self.assertIsNotNone(store)

    def test_save_and_find(self):
        store = FileInstallationStore(client_id="111.222")
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
        bot = store.find_bot(enterprise_id="E111", team_id="T222")
        self.assertIsNone(bot)
        bot = store.find_bot(enterprise_id=None, team_id="T111")
        self.assertIsNone(bot)

        i = store.find_installation(enterprise_id="E111", team_id="T111")
        self.assertIsNotNone(i)
        i = store.find_installation(enterprise_id="E111", team_id="T222")
        self.assertIsNone(i)
        i = store.find_installation(enterprise_id=None, team_id="T111")
        self.assertIsNone(i)

        i = store.find_installation(
            enterprise_id="E111", team_id="T111", user_id="U111"
        )
        self.assertIsNotNone(i)
        i = store.find_installation(
            enterprise_id="E111", team_id="T111", user_id="U222"
        )
        self.assertIsNone(i)
        i = store.find_installation(
            enterprise_id="E111", team_id="T222", user_id="U111"
        )
        self.assertIsNone(i)

    def test_org_installation(self):
        store = FileInstallationStore(client_id="111.222")
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

        bot = store.find_bot(enterprise_id="EO111", team_id=None)
        self.assertIsNotNone(bot)
        bot = store.find_bot(
            enterprise_id="EO111", team_id="TO222", is_enterprise_install=True
        )
        self.assertIsNotNone(bot)
        bot = store.find_bot(enterprise_id="EO111", team_id="TO222")
        self.assertIsNone(bot)
        bot = store.find_bot(enterprise_id=None, team_id="TO111")
        self.assertIsNone(bot)

        i = store.find_installation(enterprise_id="EO111", team_id=None)
        self.assertIsNotNone(i)
        i = store.find_installation(
            enterprise_id="EO111", team_id="T111", is_enterprise_install=True
        )
        self.assertIsNotNone(i)
        i = store.find_installation(enterprise_id="EO111", team_id="T222")
        self.assertIsNone(i)
        i = store.find_installation(enterprise_id=None, team_id="T111")
        self.assertIsNone(i)

        i = store.find_installation(
            enterprise_id="EO111", team_id=None, user_id="UO111"
        )
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
