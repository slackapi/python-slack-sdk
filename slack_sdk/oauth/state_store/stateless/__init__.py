import base64
import hashlib
import hmac as _hmac
import json
import logging
import time
from logging import Logger

from ..async_state_store import AsyncOAuthStateStore
from ..state_store import OAuthStateStore


class StatelessOAuthStateStore(OAuthStateStore, AsyncOAuthStateStore):
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
            _hmac.new(
                self.signing_secret.encode("utf-8"),
                message.encode("utf-8"),
                hashlib.sha256,
            ).digest()
        )

    def issue(self, *args, **kwargs) -> str:
        header = self._b64url_encode(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
        payload = self._b64url_encode(json.dumps({"exp": int(time.time()) + self.expiration_seconds}).encode())
        signature = self._sign(f"{header}.{payload}")
        return f"{header}.{payload}.{signature}"

    def consume(self, state: str) -> bool:
        try:
            parts = state.split(".")
            if len(parts) != 3:
                return False
            header, payload, signature = parts
            expected_signature = self._sign(f"{header}.{payload}")
            if not _hmac.compare_digest(signature, expected_signature):
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
