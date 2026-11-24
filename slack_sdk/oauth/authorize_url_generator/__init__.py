from typing import Optional, Sequence
from urllib.parse import quote


def _encode(value: str) -> str:
    # ":", "/" and "," are valid in a query component and are kept as they are,
    # so URLs built from plain values stay the same as before.
    return quote(value, safe=":/,")


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
        url = (
            f"{self.authorization_url}?"
            f"state={_encode(state)}&"
            f"client_id={_encode(self.client_id)}&"
            f"scope={_encode(scopes)}&"
            f"user_scope={_encode(user_scopes)}"
        )
        if self.redirect_uri is not None:
            url += f"&redirect_uri={_encode(self.redirect_uri)}"
        if team is not None:
            url += f"&team={_encode(team)}"
        return url


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
        url = (
            f"{self.authorization_url}?"
            "response_type=code&"
            f"state={_encode(state)}&"
            f"client_id={_encode(self.client_id)}&"
            f"scope={_encode(scopes)}&"
            f"redirect_uri={_encode(self.redirect_uri)}"
        )
        if team is not None:
            url += f"&team={_encode(team)}"
        if nonce is not None:
            url += f"&nonce={_encode(nonce)}"
        return url
