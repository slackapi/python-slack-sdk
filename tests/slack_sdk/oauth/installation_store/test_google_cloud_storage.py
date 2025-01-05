# -*- coding: utf-8 -*-
"""Tests for oauth/installation_store/google_cloud_storage/__init__.py"""

import json
import time
import logging
import unittest
from unittest.mock import Mock, call, patch
from google.cloud.storage.blob import Blob
from google.cloud.storage.bucket import Bucket

from google.cloud.storage.client import Client
from slack_sdk.oauth.installation_store.models.installation import Installation
from slack_sdk.oauth.installation_store.google_cloud_storage import GoogleCloudStorageInstallationStore


class TestGoogleInstallationStore(unittest.TestCase):
    """Tests for GoogleCloudStorageInstallationStore"""

    def setUp(self):
        """Setup test"""
        self.blob = Mock(spec=Blob)
        self.bucket = Mock(spec=Bucket)
        self.bucket.blob.return_value = self.blob

        self.storage_client = Mock(spec=Client)
        self.storage_client.bucket.return_value = self.bucket

        self.bucket_name = "bucket"
        self.client_id = "clid"
        self.logger = logging.getLogger()
        self.logger.handlers = []

        self.installation_store = GoogleCloudStorageInstallationStore(
            storage_client=self.storage_client, bucket_name=self.bucket_name, client_id=self.client_id, logger=self.logger
        )

        self.entr_installation = Installation(user_id="uid", team_id=None, is_enterprise_install=True, enterprise_id="eid")
        self.team_installation = Installation(user_id="uid", team_id="tid", is_enterprise_install=False, enterprise_id=None)

    def test_get_logger(self):
        """Test get_logger method"""
        self.assertEqual(self.installation_store.logger, self.logger)

    @patch("slack_sdk.oauth.installation_store.google_cloud_storage.GoogleCloudStorageInstallationStore._save_entity")
    def test_save_install(self, save_entity: Mock):
        """Test save method"""
        self.installation_store.save(self.entr_installation)
        self.storage_client.bucket.assert_called_once_with(self.bucket_name)
        save_entity.assert_has_calls(
            [
                call(
                    data_type="bot",
                    entity=json.dumps(self.entr_installation.to_bot().__dict__),
                    enterprise_id=self.entr_installation.enterprise_id,
                    team_id=self.entr_installation.team_id,
                    user_id=None,
                ),
                call(
                    data_type="installer",
                    entity=json.dumps(self.entr_installation.__dict__),
                    enterprise_id=self.entr_installation.enterprise_id,
                    team_id=self.entr_installation.team_id,
                    user_id=None,
                ),
                call(
                    data_type="installer",
                    entity=json.dumps(self.entr_installation.__dict__),
                    enterprise_id=self.entr_installation.enterprise_id,
                    team_id=self.entr_installation.team_id,
                    user_id=self.entr_installation.user_id,
                ),
            ]
        )

    @patch("slack_sdk.oauth.installation_store.google_cloud_storage.GoogleCloudStorageInstallationStore._save_entity")
    def test_save_bot(self, save_entity: Mock):
        """Test save_bot method"""
        self.installation_store.save_bot(bot=self.entr_installation.to_bot())
        save_entity.assert_called_once_with(
            data_type="bot",
            entity=json.dumps(self.entr_installation.to_bot().__dict__),
            enterprise_id=self.entr_installation.enterprise_id,
            team_id=self.entr_installation.team_id,
            user_id=None,
        )

    def test_save_entity_and_test_key(self):
        """Test _save_entity and _key methods"""
        entity = "some data"
        # test upload user data enterprise install + normal workspace
        for install in [self.entr_installation, self.team_installation]:
            self.installation_store._save_entity(
                data_type="dtype",
                entity=entity,
                enterprise_id=install.enterprise_id,
                team_id=install.team_id,
                user_id=install.user_id,
            )
            self.bucket.blob.assert_called_once_with(
                f"{self.client_id}/{install.enterprise_id or 'none'}-{install.team_id or 'none'}" f"/dtype-{install.user_id}"
            )
            self.blob.upload_from_string.assert_called_once_with(entity)

            self.bucket.reset_mock()

        # test upload user data enterprise install + normal workspace
        for install in [self.entr_installation, self.team_installation]:
            self.installation_store._save_entity(
                data_type="dtype", entity=entity, enterprise_id=install.enterprise_id, team_id=install.team_id, user_id=None
            )
            self.bucket.blob.assert_called_once_with(
                f"{self.client_id}/{install.enterprise_id or 'none'}-{install.team_id or 'none'}/dtype"
            )

            self.bucket.reset_mock()

    def test_find_bot(self):
        """Test find_bot method"""
        self.blob.download_as_text.return_value = json.dumps(
            {"bot_token": "xoxb-token", "bot_id": "bid", "bot_user_id": "buid", "installed_at": time.time()}
        )
        # test bot found enterprise installation + normal workspace
        for install in [self.entr_installation, self.team_installation]:
            bot = self.installation_store.find_bot(
                enterprise_id=install.enterprise_id,
                team_id=install.team_id,
                is_enterprise_install=install.is_enterprise_install,
            )
            self.storage_client.bucket.assert_called_once_with(self.bucket_name)
            self.bucket.blob.assert_called_once_with(
                f"{self.client_id}/{install.enterprise_id or 'none'}-{install.team_id or 'none'}/bot"
            )
            self.blob.download_as_text.assert_called_once_with(encoding="utf-8")
            self.assertIsNotNone(bot)
            self.assertEqual(bot.bot_token, "xoxb-token")

            self.blob.reset_mock()
            self.bucket.reset_mock()

        # test bot not found
        self.blob.download_as_text.side_effect = Exception()
        bot = self.installation_store.find_bot(
            enterprise_id=self.entr_installation.enterprise_id,
            team_id=self.entr_installation.team_id,
            is_enterprise_install=self.entr_installation.is_enterprise_install,
        )
        self.blob.download_as_text.assert_called_once_with(encoding="utf-8")
        self.assertIsNone(bot)

    def test_find_installation(self):
        """Test find_installation method"""
        self.blob.download_as_text.return_value = json.dumps({"user_id": self.entr_installation.user_id})
        # test installation found on enterprise install + normal workspace
        for expect_install in [self.entr_installation, self.team_installation]:
            actual_install = self.installation_store.find_installation(
                enterprise_id=expect_install.enterprise_id,
                team_id=expect_install.team_id,
                user_id=expect_install.user_id,
                is_enterprise_install=expect_install.is_enterprise_install,
            )
            self.storage_client.bucket.assert_called_once_with(self.bucket_name)
            self.bucket.blob.assert_called_once_with(
                f"{self.client_id}/{expect_install.enterprise_id or 'none'}-{expect_install.team_id or 'none'}/"
                f"installer-{expect_install.user_id}"
            )
            self.blob.download_as_text.assert_called_once_with(encoding="utf-8")
            self.assertIsNotNone(actual_install)
            self.assertEqual(actual_install.user_id, self.entr_installation.user_id)

            self.blob.reset_mock()
            self.bucket.reset_mock()

        # test installation not found
        self.blob.download_as_text.side_effect = Exception()
        actual_install = self.installation_store.find_installation(
            enterprise_id=self.entr_installation.enterprise_id,
            team_id=self.entr_installation.team_id,
            user_id=self.entr_installation.user_id,
            is_enterprise_install=self.entr_installation.is_enterprise_install,
        )
        self.blob.download_as_text.assert_called_once_with(encoding="utf-8")
        self.assertIsNone(actual_install)

    def test_delete_installation_and_test_delete_entity(self):
        """Test delete_installation and test_delete_entity methods"""
        self.blob.exists.return_value = True
        # test delete enterprise install + normal workspace when blob exists
        for install in [self.entr_installation, self.team_installation]:
            self.installation_store.delete_installation(
                enterprise_id=install.enterprise_id, team_id=install.team_id, user_id=install.user_id
            )
            self.storage_client.bucket.assert_called_once_with(self.bucket_name)
            self.bucket.blob.assert_called_once_with(
                f"{self.client_id}/{install.enterprise_id or 'none'}-{install.team_id or 'none'}/"
                f"installer-{self.entr_installation.user_id}"
            )
            self.blob.exists.assert_called_once()
            self.blob.delete.assert_called_once()

            self.blob.reset_mock()
            self.bucket.reset_mock()

        # test delete blob doesn't exist
        self.blob.exists.return_value = False
        self.installation_store.delete_installation(
            enterprise_id=self.entr_installation.enterprise_id,
            team_id=self.entr_installation.team_id,
            user_id=self.entr_installation.user_id,
        )
        self.blob.exists.assert_called_once()
        self.blob.delete.assert_not_called()

    @patch("slack_sdk.oauth.installation_store.google_cloud_storage.GoogleCloudStorageInstallationStore._delete_entity")
    def test_delete_bot(self, delete_entity: Mock):
        """Test delete_bot method"""
        # test delete bot from enterprise install + normal workspace
        for install in [self.entr_installation, self.team_installation]:
            self.installation_store.delete_bot(enterprise_id=install.enterprise_id, team_id=install.team_id)
            delete_entity.assert_called_once_with(
                data_type="bot", enterprise_id=install.enterprise_id, team_id=install.team_id, user_id=None
            )

            delete_entity.reset_mock()
