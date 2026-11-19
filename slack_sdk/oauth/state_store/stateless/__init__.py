import base64
import hashlib
import hmac
import json
import logging
import time
from logging import Logger

from ..async_state_store import AsyncOAuthStateStore
from ..state_store import OAuthStateStore


class StatelessOAuthStateStore(OAuthStateStore, AsyncOAuthStateStore):
    """A stateless OAuth ``state`` store backed by a signed, self-contained token.

    ``issue()`` creates an HMAC-SHA256 signed token in the JWT style. The token
    carries only an expiration claim. ``consume()`` re-verifies the signature and
    the expiry. Nothing is stored server-side. No storage backend is required.

    .. warning::
        This store provides **no one-time-use / anti-replay guarantee**. It returns
        ``True`` for the same token every time until that token expires. This is
        inherent to a stateless token. The token can only be invalidated by expiry.
        It cannot be revoked early unless you add server-side state, and that would
        defeat the point of being stateless.

        Consequences for integrators:

        - **Keep the token lifetime short.** A token stays valid until it expires.
          Use a short ``expiration_seconds``. A value of ``300`` (5 minutes) is a
          good choice and matches the OAuth sample. This limits how long a captured
          ``state`` can be replayed.
        - **Make the callback idempotent.** A captured ``state`` can be replayed
          within its lifetime. Your callback may run more than once for a single
          authorization. The ``oauth.v2.access`` exchange and the installation
          persistence must tolerate this. Slack authorization codes are single-use.
          A sequential replay fails the token exchange. The real exposure is a
          concurrent duplicate callback.
        - **CSRF protection is unchanged.** CSRF defense comes from the
          ``Secure; HttpOnly`` state cookie. ``OAuthStateUtils`` validates that cookie
          before ``consume()`` runs in the callback. Compared to the stateful stores,
          this store only gives up anti-replay and defense-in-depth. It does not give
          up CSRF protection.

    Args:
        expiration_seconds: Lifetime of an issued ``state`` token in seconds. After
            this window ``consume()`` returns ``False``. Keep this value short. A
            value of ``300`` (5 minutes) is a good default. Avoid long lifetimes.
        signing_secret: Secret used to sign and verify tokens with HMAC. Keep it
            secret. Keep it the same across every instance that must validate a
            shared token.
        logger: Logger for validation warnings.
    """

    def __init__(
        self,
        *,
        expiration_seconds: int,
        signing_secret: str,
        logger: Logger = logging.getLogger(__name__),
    ):
        self.expiration_seconds = expiration_seconds
        self.signing_secret = signing_secret
        self._logger = logger

    @property
    def logger(self) -> Logger:
        if self._logger is None:
            self._logger = logging.getLogger(__name__)
        return self._logger

    @staticmethod
    def _b64url_encode(data: bytes) -> str:
        return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")

    @staticmethod
    def _b64url_decode(data: str) -> bytes:
        padded = data + "=" * (4 - len(data) % 4)
        return base64.urlsafe_b64decode(padded)

    def _sign(self, message: str) -> str:
        return self._b64url_encode(
            hmac.new(
                self.signing_secret.encode("utf-8"),
                message.encode("utf-8"),
                hashlib.sha256,
            ).digest()
        )

    def issue(self, *args, **kwargs) -> str:
        header = self._b64url_encode(json.dumps({"alg": "HS256", "typ": "JWT"}, separators=(",", ":")).encode())
        payload = self._b64url_encode(
            json.dumps({"exp": int(time.time()) + self.expiration_seconds}, separators=(",", ":")).encode()
        )
        signature = self._sign(f"{header}.{payload}")
        return f"{header}.{payload}.{signature}"

    def consume(self, state: str) -> bool:
        """Validate a ``state`` token's signature and ``expiration`` claim.

        Returns ``True`` for any correctly signed, unexpired token, **every time**.
        This store keeps no record of consumed tokens. It does not enforce
        one-time-use. See the class docstring for the anti-replay caveat.
        """
        try:
            parts = state.split(".")
            if len(parts) != 3:
                return False
            header, payload, signature = parts
            expected_signature = self._sign(f"{header}.{payload}")
            if not hmac.compare_digest(signature, expected_signature):
                self.logger.warning("Invalid JWT signature for state parameter")
                return False
            claims = json.loads(self._b64url_decode(payload))
            exp = claims.get("exp")
            if exp is None or time.time() > exp:
                self.logger.warning("Expired or missing exp claim in state JWT")
                return False
            return True
        except Exception as e:
            self.logger.warning(f"Failed to validate state JWT: {e}")
            return False

    async def async_issue(self, *args, **kwargs) -> str:
        return self.issue(*args, **kwargs)

    async def async_consume(self, state: str) -> bool:
        return self.consume(state)
