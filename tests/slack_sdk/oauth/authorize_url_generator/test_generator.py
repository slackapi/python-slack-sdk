import unittest
import uuid
from urllib.parse import parse_qs, urlparse

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

    def test_redirect_uri_with_query_string(self):
        redirect_uri = "https://www.example.com/slack/oauth_redirect?tenant=acme&env=prod"
        generator = AuthorizeUrlGenerator(
            client_id="111.222",
            scopes=["chat:write"],
            redirect_uri=redirect_uri,
        )
        url = generator.generate("state-value")
        expected = (
            "https://slack.com/oauth/v2/authorize"
            "?state=state-value"
            "&client_id=111.222"
            "&scope=chat:write"
            "&user_scope="
            "&redirect_uri=https://www.example.com/slack/oauth_redirect%3Ftenant%3Dacme%26env%3Dprod"
        )
        self.assertEqual(expected, url)

        params = parse_qs(urlparse(url).query, keep_blank_values=True)
        self.assertEqual([redirect_uri], params["redirect_uri"])
        self.assertNotIn("env", params)

    def test_state_and_team_with_reserved_characters(self):
        generator = AuthorizeUrlGenerator(client_id="111.222", scopes=["chat:write"])
        url = generator.generate(state="a+b/c==", team="T1&x=1")

        params = parse_qs(urlparse(url).query, keep_blank_values=True)
        self.assertEqual(["a+b/c=="], params["state"])
        self.assertEqual(["T1&x=1"], params["team"])
        self.assertNotIn("x", params)

    def test_openid_connect_with_reserved_characters(self):
        redirect_uri = "https://www.example.com/oidc/callback?tenant=acme&env=prod"
        generator = OpenIDConnectAuthorizeUrlGenerator(
            client_id="111.222",
            redirect_uri=redirect_uri,
            scopes=["openid"],
        )
        url = generator.generate(state="a+b/c==", nonce="n+1&x=1", team="T12345")

        params = parse_qs(urlparse(url).query, keep_blank_values=True)
        self.assertEqual([redirect_uri], params["redirect_uri"])
        self.assertEqual(["a+b/c=="], params["state"])
        self.assertEqual(["n+1&x=1"], params["nonce"])
        self.assertEqual(["T12345"], params["team"])
        self.assertNotIn("env", params)
        self.assertNotIn("x", params)

    def test_non_str_values(self):
        state = uuid.uuid4()
        generator = AuthorizeUrlGenerator(client_id=111222, scopes=["chat:write"])
        url = generator.generate(state=state)

        params = parse_qs(urlparse(url).query, keep_blank_values=True)
        self.assertEqual([str(state)], params["state"])
        self.assertEqual(["111222"], params["client_id"])

    def test_openid_connect_with_non_str_values(self):
        state = uuid.uuid4()
        generator = OpenIDConnectAuthorizeUrlGenerator(
            client_id="111.222",
            redirect_uri="https://www.example.com/oidc/callback",
            scopes=["openid"],
        )
        url = generator.generate(state=state, nonce=uuid.UUID(int=1))

        params = parse_qs(urlparse(url).query, keep_blank_values=True)
        self.assertEqual([str(state)], params["state"])
        self.assertEqual(["00000000-0000-0000-0000-000000000001"], params["nonce"])
