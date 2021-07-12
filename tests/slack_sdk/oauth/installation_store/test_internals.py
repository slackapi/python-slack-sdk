import unittest

from slack_sdk.oauth.installation_store import Installation, FileInstallationStore
from slack_sdk.oauth.installation_store.internals import _from_iso_format_to_datetime


class TestFile(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_iso_format(self):
        dt = _from_iso_format_to_datetime("2021-07-14 08:00:17")
        self.assertEqual(dt.timestamp(), 1626249617.0)
