from typing import Optional, Sequence


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

    def generate(self, state: str):
        scopes = ",".join(self.scopes) if self.scopes else ""
        user_scopes = ",".join(self.user_scopes) if self.user_scopes else ""
        url = (
            f"{self.authorization_url}?"
            f"state={state}&"
            f"client_id={self.client_id}&"
            f"scope={scopes}&"
            f"user_scope={user_scopes}"
        )
        if self.redirect_uri is not None:
            url += f"&redirect_uri={self.redirect_uri}"
        return url
