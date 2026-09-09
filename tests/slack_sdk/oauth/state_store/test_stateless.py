import unittest

from slack_sdk.oauth.state_store import StatelessOAuthStateStore


class TestStateless(unittest.TestCase):
    def setUp(self):
        self.store = StatelessOAuthStateStore(
            expiration_seconds=10,
            signing_secret="test-signing-secret",
        )

    def tearDown(self):
        pass

    def test_instance(self):
        self.assertIsNotNone(self.store)

    def test_issue_returns_jwt_format(self):
        state = self.store.issue()
        self.assertEqual(len(state.split(".")), 3)

    def test_issue_and_consume(self):
        state = self.store.issue()
        result = self.store.consume(state)
        self.assertTrue(result)

    def test_consume_is_repeatable(self):
        state = self.store.issue()
        self.assertTrue(self.store.consume(state))
        self.assertTrue(self.store.consume(state))

    def test_invalid_state_format(self):
        self.assertFalse(self.store.consume("not-a-jwt"))

    def test_tampered_signature(self):
        state = self.store.issue()
        parts = state.split(".")
        parts[2] = "invalidsignature"
        self.assertFalse(self.store.consume(".".join(parts)))

    def test_tampered_payload(self):
        state = self.store.issue()
        parts = state.split(".")
        parts[1] = parts[1][:-2] + "AA"
        self.assertFalse(self.store.consume(".".join(parts)))

    def test_wrong_signing_secret(self):
        store2 = StatelessOAuthStateStore(
            expiration_seconds=10,
            signing_secret="different-secret",
        )
        state = self.store.issue()
        self.assertFalse(store2.consume(state))

    def test_expired_state(self):
        expired_store = StatelessOAuthStateStore(
            expiration_seconds=-1,
            signing_secret="test-signing-secret",
        )
        state = expired_store.issue()
        self.assertFalse(self.store.consume(state))

    def test_kwargs(self):
        self.store.issue(foo=123, bar="baz")
