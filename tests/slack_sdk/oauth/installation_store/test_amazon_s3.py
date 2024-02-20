import unittest

import boto3

try:
    from moto import mock_aws
except ImportError:
    from moto import mock_s3 as mock_aws
from slack_sdk.oauth.installation_store import Installation
from slack_sdk.oauth.installation_store.amazon_s3 import AmazonS3InstallationStore


class TestAmazonS3(unittest.TestCase):
    mock_aws = mock_aws()
    bucket_name = "test-bucket"

    def setUp(self):
        self.mock_aws.start()
        s3 = boto3.resource("s3")
        bucket = s3.Bucket(self.bucket_name)
        bucket.create(CreateBucketConfiguration={"LocationConstraint": "af-south-1"})

    def tearDown(self):
        self.mock_aws.stop()

    def build_store(self) -> AmazonS3InstallationStore:
        return AmazonS3InstallationStore(
            s3_client=boto3.client("s3"),
            bucket_name=self.bucket_name,
            client_id="111.222",
        )

    def test_instance(self):
        store = self.build_store()
        self.assertIsNotNone(store)

    def test_save_and_find(self):
        store = self.build_store()
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
        store = self.build_store()
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
        store.delete_installation(enterprise_id="E111", team_id=None)
        i = store.find_installation(enterprise_id="E111", team_id=None)
        self.assertIsNone(i)

        # delete all
        store.save(installation)
        store.delete_all(enterprise_id="E111", team_id=None)

        i = store.find_installation(enterprise_id="E111", team_id=None)
        self.assertIsNone(i)
        i = store.find_installation(enterprise_id="E111", team_id=None, user_id="U111")
        self.assertIsNone(i)
        bot = store.find_bot(enterprise_id=None, team_id="T222")
        self.assertIsNone(bot)

    def test_save_and_find_token_rotation(self):
        store = self.build_store()
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
        store = self.build_store()

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
