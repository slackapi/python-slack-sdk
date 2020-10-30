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
            scopes=["chat:write", "commands"],
            user_scopes=["search:read"],
        )
        url = generator.generate("state-value")
        expected = "https://slack.com/oauth/v2/authorize?state=state-value&client_id=111.222&scope=chat:write,commands&user_scope=search:read"
        self.assertEqual(expected, url)
