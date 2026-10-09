import unittest
from urllib.parse import parse_qs, urlsplit

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

    def test_query_parameters_round_trip(self):
        redirect_uri = "https://www.example.com/callback?view=home&lang=en"
        generator = AuthorizeUrlGenerator(
            client_id="111.222",
            redirect_uri=redirect_uri,
            scopes=["chat:write", "commands"],
            user_scopes=["search:read"],
        )
        for state in (
            "",
            "plus+value",
            "space value",
            "key=value&other=value",
            "percent%20value",
            "fragment#value",
            "日本語",
        ):
            with self.subTest(state=state):
                url = generator.generate(state=state, team="T12345")
                self.assertDictEqual(
                    {
                        "state": [state],
                        "client_id": ["111.222"],
                        "scope": ["chat:write,commands"],
                        "user_scope": ["search:read"],
                        "redirect_uri": [redirect_uri],
                        "team": ["T12345"],
                    },
                    parse_qs(urlsplit(url).query, keep_blank_values=True),
                )

    def test_openid_connect_query_parameters_round_trip(self):
        redirect_uri = "https://www.example.com/oidc/callback?view=home%20page&lang=en"
        generator = OpenIDConnectAuthorizeUrlGenerator(
            client_id="111.222",
            redirect_uri=redirect_uri,
            scopes=["openid", "profile"],
        )
        for value in (
            "",
            "plus+value",
            "space value",
            "key=value&other=value",
            "percent%20value",
            "fragment#value",
            "日本語",
        ):
            with self.subTest(value=value):
                state = f"state-{value}"
                url = generator.generate(state=state, nonce=value, team="T12345")
                self.assertDictEqual(
                    {
                        "response_type": ["code"],
                        "state": [state],
                        "client_id": ["111.222"],
                        "scope": ["openid,profile"],
                        "redirect_uri": [redirect_uri],
                        "team": ["T12345"],
                        "nonce": [value],
                    },
                    parse_qs(urlsplit(url).query, keep_blank_values=True),
                )

    def test_pre_encoded_authorization_values_are_not_decoded(self):
        redirect_uri = "https://www.example.com/callback%3Fa%3Db"
        generator = AuthorizeUrlGenerator(
            client_id="111.222", redirect_uri=redirect_uri
        )
        url = generator.generate(state="abc%2B")
        self.assertIn("state=abc%252B", url)
        self.assertIn("redirect_uri=https://www.example.com/callback%253Fa%253Db", url)

        openid_generator = OpenIDConnectAuthorizeUrlGenerator(
            client_id="111.222", redirect_uri=redirect_uri
        )
        url = openid_generator.generate(state="abc%2B", nonce="x%26y")
        self.assertIn("state=abc%252B", url)
        self.assertIn("redirect_uri=https://www.example.com/callback%253Fa%253Db", url)
        self.assertIn("nonce=x%2526y", url)
