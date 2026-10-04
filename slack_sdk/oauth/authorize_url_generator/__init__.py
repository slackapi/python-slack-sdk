from typing import Optional, Sequence
from urllib.parse import urlencode


class AuthorizeUrlGenerator:
    def __init__(
        self,
        *,
        client_id: str,
        redirect_uri: Optional[str] = None,
        scopes: Optional[Sequence[str]] = None,
        user_scopes: Optional[Sequence[str]] = None,
        authorization_url: str = "https://slack.com/oauth/v2/authorize",
    ):
        self.client_id = client_id
        self.redirect_uri = redirect_uri
        self.scopes = scopes
        self.user_scopes = user_scopes
        self.authorization_url = authorization_url

    def generate(self, state: str, team: Optional[str] = None) -> str:
        scopes = ",".join(self.scopes) if self.scopes else ""
        user_scopes = ",".join(self.user_scopes) if self.user_scopes else ""
        params = {
            "state": state,
            "client_id": self.client_id,
            "scope": scopes,
            "user_scope": user_scopes,
        }
        if self.redirect_uri is not None:
            params["redirect_uri"] = self.redirect_uri
        if team is not None:
            params["team"] = team
        query = urlencode(params, safe=":,/")
        return f"{self.authorization_url}?{query}"


class OpenIDConnectAuthorizeUrlGenerator:
    """Refer to https://openid.net/specs/openid-connect-core-1_0.html."""

    def __init__(
        self,
        *,
        client_id: str,
        redirect_uri: str,
        scopes: Optional[Sequence[str]] = None,
        authorization_url: str = "https://slack.com/openid/connect/authorize",
    ):
        self.client_id = client_id
        self.redirect_uri = redirect_uri
        self.scopes = scopes
        self.authorization_url = authorization_url

    def generate(self, state: str, nonce: Optional[str] = None, team: Optional[str] = None) -> str:
        scopes = ",".join(self.scopes) if self.scopes else ""
        params = {
            "response_type": "code",
            "state": state,
            "client_id": self.client_id,
            "scope": scopes,
            "redirect_uri": self.redirect_uri,
        }
        if team is not None:
            params["team"] = team
        if nonce is not None:
            params["nonce"] = nonce
        query = urlencode(params, safe=":,/")
        return f"{self.authorization_url}?{query}"
