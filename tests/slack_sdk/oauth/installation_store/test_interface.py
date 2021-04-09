import unittest

from slack_sdk.oauth.installation_store import InstallationStore
from slack_sdk.oauth.installation_store.async_installation_store import (
    AsyncInstallationStore,
)


class TestInterface(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_sync(self):
        store = InstallationStore()
        self.assertIsNotNone(store)

    def test_async(self):
        store = AsyncInstallationStore()
        self.assertIsNotNone(store)
