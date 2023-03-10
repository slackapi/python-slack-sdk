import unittest

from slack_sdk.oauth import AuthorizeUrlGenerator, OpenIDConnectAuthorizeUrlGenerator


class TestGenerator(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_default(self):
        generator = AuthorizeUrlGenerator(
            client_id="111.222",
            scopes=["chat:write", "commands"],
            user_scopes=["search:read"],
        )
        url = generator.generate("state-value")
        expected = "https://slack.com/oauth/v2/authorize?state=state-value&client_id=111.222&scope=chat:write,commands&user_scope=search:read"
        self.assertEqual(expected, url)

    def test_base_url(self):
        generator = AuthorizeUrlGenerator(
            client_id="111.222",
            scopes=["chat:write", "commands"],
            user_scopes=["search:read"],
            authorization_url="https://www.example.com/authorize",
        )
        url = generator.generate("state-value")
        expected = (
            "https://www.example.com/authorize"
            "?state=state-value"
            "&client_id=111.222"
            "&scope=chat:write,commands"
            "&user_scope=search:read"
        )
        self.assertEqual(expected, url)

    def test_team(self):
        generator = AuthorizeUrlGenerator(
            client_id="111.222",
            scopes=["chat:write", "commands"],
            user_scopes=["search:read"],
        )
        url = generator.generate(state="state-value", team="T12345")
        expected = (
            "https://slack.com/oauth/v2/authorize"
            "?state=state-value"
            "&client_id=111.222"
            "&scope=chat:write,commands&user_scope=search:read"
            "&team=T12345"
        )
        self.assertEqual(expected, url)

    def test_openid_connect(self):
        generator = OpenIDConnectAuthorizeUrlGenerator(
            client_id="111.222",
            redirect_uri="https://www.example.com/oidc/callback",
            scopes=["openid"],
        )
        url = generator.generate(state="state-value", nonce="nnn", team="T12345")
        expected = (
            "https://slack.com/openid/connect/authorize"
            "?response_type=code&state=state-value"
            "&client_id=111.222"
            "&scope=openid"
            "&redirect_uri=https://www.example.com/oidc/callback"
            "&team=T12345"
            "&nonce=nnn"
        )
        self.assertEqual(expected, url)
