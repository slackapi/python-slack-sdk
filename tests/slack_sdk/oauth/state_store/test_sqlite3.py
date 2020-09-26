import unittest

from slack_sdk.oauth.state_store.sqlite3 import SQLite3OAuthStateStore


class TestSQLite3(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_instance(self):
        store = SQLite3OAuthStateStore(
            database="logs/test.db",
            expiration_seconds=10,
        )
        self.assertIsNotNone(store)

    def test_issue_and_consume(self):
        store = SQLite3OAuthStateStore(
            database="logs/test.db",
            expiration_seconds=10,
        )
        state = store.issue()
        result = store.consume(state)
        self.assertTrue(result)
        result = store.consume(state)
        self.assertFalse(result)
