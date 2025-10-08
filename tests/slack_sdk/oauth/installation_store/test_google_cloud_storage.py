# -*- coding: utf-8 -*-
"""Tests for oauth/installation_store/google_cloud_storage/__init__.py"""

import unittest
from unittest.mock import Mock
from google.cloud.storage.blob import Blob
from google.cloud.storage.bucket import Bucket

from google.cloud.storage.client import Client
from slack_sdk.oauth.installation_store.models.installation import Installation
from slack_sdk.oauth.installation_store.google_cloud_storage import GoogleCloudStorageInstallationStore


class CloudStorageMockRecorder:
    def __init__(self):
        self.storage = {}  # simulate cloud storage

    def mock_bucket_method(self, method_name: str):
        """Mock bucket blob creation"""

        def wrapper(*args, **kwargs):
            if method_name == "blob":
                return self._make_blob_mock(args[0])  # make mock with the blob path when one is created
            elif method_name == "list_blobs":
                prefix = kwargs.get("prefix", "")
                blob_names = [  # check how many recorded blobs start with the prefix
                    blob_name for blob_name in self.storage.keys() if blob_name.startswith(prefix)
                ]
                # return list of mocked blobs with the matched names
                return [self._make_blob_mock(blob_name) for blob_name in blob_names]

        return wrapper

    def mock_blob_method(self, blob_name: str, method_name: str):
        """Record blob activity"""

        def wrapper(*args, **kwargs):
            if method_name == "upload_from_string":
                self.storage[blob_name] = args[0]  # blob value
            elif method_name == "download_as_text":
                return self.storage.get(blob_name, None)  # return saved blob data or None
            elif method_name == "delete":
                self.storage.pop(blob_name, None)  # remove saved blob if it exists

        return wrapper

    def _make_blob_mock(self, blob_name: str) -> Mock:
        """Helper method to make a `Mock` of a `Blob`"""
        blob_mock = Mock(spec=Blob)
        blob_mock.name = blob_name
        blob_mock.upload_from_string.side_effect = self.mock_blob_method(blob_name, "upload_from_string")
        blob_mock.download_as_text.side_effect = self.mock_blob_method(blob_name, "download_as_text")
        blob_mock.delete.side_effect = self.mock_blob_method(blob_name, "delete")
        return blob_mock


class TestGoogleInstallationStore(unittest.TestCase):
    def setUp(self):
        # self.blob = Mock(spec=Blob)
        self.bucket = Mock(spec=Bucket)
        recorder = CloudStorageMockRecorder()

        self.bucket.blob.side_effect = recorder.mock_bucket_method("blob")
        self.bucket.list_blobs.side_effect = recorder.mock_bucket_method("list_blobs")

        self.storage_client = Mock(spec=Client)
        self.storage_client.bucket.return_value = self.bucket

    def _build_store(self) -> GoogleCloudStorageInstallationStore:
        return GoogleCloudStorageInstallationStore(
            storage_client=self.storage_client, bucket_name="bucket_name", client_id="client_id"
        )

    def test_instance(self):
        self.assertIsNotNone(self._build_store())

    def test_save_and_find(self):
        store = self._build_store()
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
        store = self._build_store()
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
        store = self._build_store()
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
        store = self._build_store()

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
