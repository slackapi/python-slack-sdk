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

    body = "token=xyzz0WbapA4vBCDEFasx0q6G&team_id=T1DC2JH3J&team_domain=testteamnow&channel_id=G8PSS9T3V&channel_name=foobar&user_id=U2CERLKJA&user_name=roadrunner&command=%2Fwebhook-collect&text=&response_url=https%3A%2F%2Fhooks.slack.com%2Fcommands%2FT1DC2JH3J%2F397700885554%2F96rGlfmibIGlgcZRskXaIFfN&trigger_id=398738663015.47445629121.803a0bc887a14d10d2c447fce8b6703c"
    headers = {
        "X-Slack-Request-Timestamp": "1531420618",
        "X-Slack-Signature": "v0=a2114d57b48eac39b9ad189dd8316235a7b4a8d21a10bd27519666489c69b503",
    }

    def test_generate_signature(self):
        # https://api.slack.com/authentication/verifying-requests-from-slack
        verifier = SignatureVerifier("8f742231b10e8888abcd99yyyzzz85a5")
        timestamp = "1531420618"
        signature = verifier.generate_signature(timestamp=timestamp, body=self.body)
        self.assertEqual("v0=a2114d57b48eac39b9ad189dd8316235a7b4a8d21a10bd27519666489c69b503", signature)

    def test_is_valid_request(self):
        verifier = SignatureVerifier(
            signing_secret="8f742231b10e8888abcd99yyyzzz85a5",
            clock=MockClock()
        )
        self.assertTrue(verifier.is_valid_request(self.body, self.headers))

    def test_is_valid_request_invalid_body(self):
        verifier = SignatureVerifier(
            signing_secret="8f742231b10e8888abcd99yyyzzz85a5",
            clock=MockClock()
        )
        modified_body = self.body + "------"
        self.assertFalse(verifier.is_valid_request(modified_body, self.headers))

    def test_is_valid_request_expiration(self):
        verifier = SignatureVerifier(
            signing_secret="8f742231b10e8888abcd99yyyzzz85a5"
        )
        self.assertFalse(verifier.is_valid_request(self.body, self.headers))
