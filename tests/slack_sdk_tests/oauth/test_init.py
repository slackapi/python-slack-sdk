import unittest

from slack_sdk.oauth import AuthorizeUrlGenerator

class TestInit(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_generator(self):
        generator = AuthorizeUrlGenerator(
            client_id="111.222",
            client_secret="xxx"
        )
        url = generator.generate("state-value")
        expected = "https://slack.com/oauth/v2/authorize?state=state-value&client_id=111.222&scope=&user_scope="
        self.assertEqual(expected, url)