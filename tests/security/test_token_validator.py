import time
from collections.abc import Generator

import jwt
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from pilot_api.security.token_validator import TokenValidationError, TokenValidator

_ISSUER = "https://issuer.test/realms/local-realm"


@pytest.fixture(scope="module")
def keypair() -> Generator[tuple[bytes, bytes], None, None]:
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    public_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    yield private_pem, public_pem


def _make_validator(
    public_pem: bytes, *, issuer: str = _ISSUER, audience: str | None = None
) -> TokenValidator:
    return TokenValidator(
        jwks_url="unused://jwks",
        issuer=issuer,
        audience=audience,
        cache_seconds=60,
        signing_key_resolver=lambda _raw_token: public_pem,
    )


def _make_token(
    private_pem: bytes,
    *,
    issuer: str = _ISSUER,
    audience: str | None = None,
    exp_delta: int = 3600,
    **extra_claims: object,
) -> str:
    now = int(time.time())
    claims: dict[str, object] = {"iss": issuer, "iat": now, "exp": now + exp_delta, **extra_claims}
    if audience:
        claims["aud"] = audience
    return jwt.encode(claims, private_pem, algorithm="RS256")


def test_decode_returns_claims_for_a_valid_token(keypair: tuple[bytes, bytes]) -> None:
    private_pem, public_pem = keypair
    validator = _make_validator(public_pem)
    token = _make_token(private_pem, preferred_username="working_admin_user")

    claims = validator.decode(token)

    assert claims["preferred_username"] == "working_admin_user"
    assert claims["iss"] == _ISSUER


def test_decode_raises_for_expired_token(keypair: tuple[bytes, bytes]) -> None:
    private_pem, public_pem = keypair
    validator = _make_validator(public_pem)
    token = _make_token(private_pem, exp_delta=-10)

    with pytest.raises(TokenValidationError):
        validator.decode(token)


def test_decode_raises_for_wrong_issuer(keypair: tuple[bytes, bytes]) -> None:
    private_pem, public_pem = keypair
    validator = _make_validator(public_pem, issuer=_ISSUER)
    token = _make_token(private_pem, issuer="https://other-issuer.test/realms/other")

    with pytest.raises(TokenValidationError):
        validator.decode(token)


def test_decode_raises_for_wrong_audience_when_audience_is_configured(
    keypair: tuple[bytes, bytes],
) -> None:
    private_pem, public_pem = keypair
    validator = _make_validator(public_pem, audience="expected-client")
    token = _make_token(private_pem, audience="unexpected-client")

    with pytest.raises(TokenValidationError):
        validator.decode(token)


def test_decode_ignores_audience_when_not_configured(keypair: tuple[bytes, bytes]) -> None:
    private_pem, public_pem = keypair
    validator = _make_validator(public_pem, audience=None)
    token = _make_token(private_pem, audience="whatever")

    claims = validator.decode(token)

    assert claims["aud"] == "whatever"


def test_decode_raises_when_signing_key_cannot_be_resolved() -> None:
    def failing_resolver(_raw_token: str) -> bytes:
        raise RuntimeError("no matching key")

    validator = TokenValidator(
        jwks_url="unused://jwks",
        issuer=_ISSUER,
        audience=None,
        cache_seconds=60,
        signing_key_resolver=failing_resolver,
    )

    with pytest.raises(TokenValidationError):
        validator.decode("not-a-real-token")
