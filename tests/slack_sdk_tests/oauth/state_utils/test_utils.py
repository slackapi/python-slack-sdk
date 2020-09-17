import unittest

from slack_sdk.oauth import OAuthStateUtils


class TestUtils(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_is_valid_browser(self):
        utils = OAuthStateUtils()
        cookie_name = OAuthStateUtils.default_cookie_name
        result = utils.is_valid_browser("state-value", {"cookie": f"{cookie_name}=state-value"})
        self.assertTrue(result)
        result = utils.is_valid_browser("state-value", {"cookie": f"{cookie_name}=xxx"})
        self.assertFalse(result)

        result = utils.is_valid_browser("state-value", {"cookie": [f"{cookie_name}=state-value"]})
        self.assertTrue(result)
        result = utils.is_valid_browser("state-value", {"cookie": [f"{cookie_name}=xxx"]})
        self.assertFalse(result)

    def test_build_set_cookie_for_new_state(self):
        utils = OAuthStateUtils()
        value = utils.build_set_cookie_for_new_state("state-value")
        expected = "slack-app-oauth-state=state-value; Secure; HttpOnly; Path=/; Max-Age=600"
        self.assertEqual(expected, value)

    def test_build_set_cookie_for_deletion(self):
        utils = OAuthStateUtils()
        value = utils.build_set_cookie_for_deletion()
        expected = "slack-app-oauth-state=deleted; Secure; HttpOnly; Path=/; Expires=Thu, 01 Jan 1970 00:00:00 GMT"
        self.assertEqual(expected, value)
