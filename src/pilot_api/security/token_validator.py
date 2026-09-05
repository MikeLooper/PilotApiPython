from collections.abc import Callable
from typing import Any

import jwt
from jwt import PyJWKClient


class TokenValidationError(Exception):
    def __init__(self, reason: str):
        super().__init__(reason)
        self.reason = reason


class TokenValidator:
    """Verifies JWT signature (via JWKS), issuer, audience, and expiry."""

    def __init__(
        self,
        *,
        jwks_url: str,
        issuer: str,
        audience: str | None,
        cache_seconds: int,
        signing_key_resolver: Callable[[str], Any] | None = None,
    ):
        self._issuer = issuer
        self._audience = audience
        self._signing_key_resolver = signing_key_resolver or PyJWKClient(
            jwks_url, lifespan=cache_seconds
        ).get_signing_key_from_jwt

    def decode(self, raw_token: str) -> dict[str, Any]:
        try:
            signing_key = self._signing_key_resolver(raw_token)
            key = signing_key.key if hasattr(signing_key, "key") else signing_key
            return jwt.decode(
                raw_token,
                key,
                algorithms=["RS256"],
                issuer=self._issuer,
                audience=self._audience,
                options={"verify_aud": self._audience is not None},
            )
        except jwt.ExpiredSignatureError as exc:
            raise TokenValidationError("token expired") from exc
        except jwt.InvalidTokenError as exc:
            raise TokenValidationError(f"invalid token: {exc}") from exc
        except Exception as exc:
            raise TokenValidationError(f"unable to resolve signing key: {exc}") from exc
