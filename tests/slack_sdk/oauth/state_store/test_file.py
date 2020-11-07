import unittest

from slack_sdk.oauth.state_store import FileOAuthStateStore


class TestFile(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_instance(self):
        store = FileOAuthStateStore(expiration_seconds=10)
        self.assertIsNotNone(store)

    def test_issue_and_consume(self):
        store = FileOAuthStateStore(expiration_seconds=10)
        state = store.issue()
        result = store.consume(state)
        self.assertTrue(result)
        result = store.consume(state)
        self.assertFalse(result)

    def test_kwargs(self):
        store = FileOAuthStateStore(expiration_seconds=10)
        store.issue(foo=123, bar="baz")
