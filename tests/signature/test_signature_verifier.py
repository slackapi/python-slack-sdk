import unittest

from slack.signature import SignatureVerifier


class MockClock:
    def now(self) -> float:
        return 1531420618


class TestSignatureVerifier(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    # https://docs.slack.dev/authentication/verifying-requests-from-slack/
    signing_secret = "8f742231b10e8888abcd99yyyzzz85a5"

    body = "token=xyzz0WbapA4vBCDEFasx0q6G&team_id=T1DC2JH3J&team_domain=testteamnow&channel_id=G8PSS9T3V&channel_name=foobar&user_id=U2CERLKJA&user_name=roadrunner&command=%2Fwebhook-collect&text=&response_url=https%3A%2F%2Fhooks.slack.com%2Fcommands%2FT1DC2JH3J%2F397700885554%2F96rGlfmibIGlgcZRskXaIFfN&trigger_id=398738663015.47445629121.803a0bc887a14d10d2c447fce8b6703c"

    timestamp = "1531420618"
    valid_signature = "v0=a2114d57b48eac39b9ad189dd8316235a7b4a8d21a10bd27519666489c69b503"

    headers = {
        "X-Slack-Request-Timestamp": timestamp,
        "X-Slack-Signature": valid_signature,
    }

    def test_generate_signature(self):
        verifier = SignatureVerifier(self.signing_secret)
        signature = verifier.generate_signature(timestamp=self.timestamp, body=self.body)
        self.assertEqual(self.valid_signature, signature)

    def test_generate_signature_body_as_bytes(self):
        verifier = SignatureVerifier(self.signing_secret)
        signature = verifier.generate_signature(timestamp=self.timestamp, body=self.body.encode("utf-8"))
        self.assertEqual(self.valid_signature, signature)

    def test_is_valid_request(self):
        verifier = SignatureVerifier(signing_secret=self.signing_secret, clock=MockClock())
        self.assertTrue(verifier.is_valid_request(self.body, self.headers))

    def test_is_valid_request_body_as_bytes(self):
        verifier = SignatureVerifier(signing_secret=self.signing_secret, clock=MockClock())
        self.assertTrue(verifier.is_valid_request(self.body.encode("utf-8"), self.headers))

    def test_is_valid_request_invalid_body(self):
        verifier = SignatureVerifier(
            signing_secret=self.signing_secret,
            clock=MockClock(),
        )
        modified_body = self.body + "------"
        self.assertFalse(verifier.is_valid_request(modified_body, self.headers))

    def test_is_valid_request_invalid_body_as_bytes(self):
        verifier = SignatureVerifier(
            signing_secret=self.signing_secret,
            clock=MockClock(),
        )
        modified_body = self.body + "------"
        self.assertFalse(verifier.is_valid_request(modified_body.encode("utf-8"), self.headers))

    def test_is_valid_request_expiration(self):
        verifier = SignatureVerifier(
            signing_secret=self.signing_secret,
        )
        self.assertFalse(verifier.is_valid_request(self.body, self.headers))

    def test_is_valid_request_none(self):
        verifier = SignatureVerifier(
            signing_secret=self.signing_secret,
            clock=MockClock(),
        )
        self.assertFalse(verifier.is_valid_request(None, self.headers))
        self.assertFalse(verifier.is_valid_request(self.body, None))
        self.assertFalse(verifier.is_valid_request(None, None))

    def test_is_valid(self):
        verifier = SignatureVerifier(
            signing_secret=self.signing_secret,
            clock=MockClock(),
        )
        self.assertTrue(verifier.is_valid(self.body, self.timestamp, self.valid_signature))
        self.assertTrue(verifier.is_valid(self.body, 1531420618, self.valid_signature))

    def test_is_valid_none(self):
        verifier = SignatureVerifier(
            signing_secret=self.signing_secret,
            clock=MockClock(),
        )
        self.assertFalse(verifier.is_valid(None, self.timestamp, self.valid_signature))
        self.assertFalse(verifier.is_valid(self.body, None, self.valid_signature))
        self.assertFalse(verifier.is_valid(self.body, self.timestamp, None))
        self.assertFalse(verifier.is_valid(None, None, self.valid_signature))
        self.assertFalse(verifier.is_valid(None, self.timestamp, None))
        self.assertFalse(verifier.is_valid(self.body, None, None))
        self.assertFalse(verifier.is_valid(None, None, None))
