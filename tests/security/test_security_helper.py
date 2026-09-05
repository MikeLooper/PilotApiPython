import asyncio
from types import SimpleNamespace
from typing import Any

import pytest

from pilot_api.config.settings import Settings
from pilot_api.exception.errors import ForbiddenError, UnauthorizedError
from pilot_api.security.role_repository import UserRoleRepository
from pilot_api.security.security_helper import SecurityHelper
from pilot_api.security.token_validator import TokenValidationError


class _FakeUrl:
    def __init__(self, path: str):
        self.path = path


class _FakeRequest:
    def __init__(
        self,
        method: str = "GET",
        path: str = "/v1/categories/get-all",
        headers: dict | None = None,
    ):
        self.method = method
        self.url = _FakeUrl(path)
        self.headers = headers or {}
        self.state = SimpleNamespace(request_id="req-1", correlation_id="corr-1")


class _FakeResponse:
    def __init__(self) -> None:
        self.headers: dict[str, str] = {}


class _StubTokenValidator:
    def __init__(self, claims_by_token: dict[str, dict[str, Any]]):
        self._claims_by_token = claims_by_token

    def decode(self, raw_token: str) -> dict[str, Any]:
        claims = self._claims_by_token.get(raw_token)
        if claims is None:
            raise TokenValidationError("unknown test token")
        return claims


def _run(coro):
    return asyncio.run(coro)


def _make_helper(
    security_active: bool, claims_by_token: dict[str, dict[str, Any]]
) -> SecurityHelper:
    return SecurityHelper(
        settings=Settings(security_active=security_active),
        token_validator=_StubTokenValidator(claims_by_token),
        role_repository=UserRoleRepository(),
    )


def test_enforce_blocks_missing_token_when_active() -> None:
    helper = _make_helper(True, {})

    with pytest.raises(UnauthorizedError):
        _run(helper.enforce(_FakeRequest(), _FakeResponse()))


def test_enforce_allows_missing_token_when_inactive_and_sets_warning_header() -> None:
    helper = _make_helper(False, {})
    response = _FakeResponse()

    context = _run(helper.enforce(_FakeRequest(), response))

    assert context.is_authenticated is False
    assert "Warning" in response.headers


def test_enforce_blocks_insufficient_role_when_active() -> None:
    helper = _make_helper(True, {"reader-token": {"preferred_username": "reader_user"}})
    request = _FakeRequest(method="POST", headers={"Authorization": "Bearer reader-token"})

    with pytest.raises(ForbiddenError):
        _run(helper.enforce(request, _FakeResponse()))


def test_enforce_allows_insufficient_role_when_inactive_and_sets_warning_header() -> None:
    helper = _make_helper(False, {"reader-token": {"preferred_username": "reader_user"}})
    request = _FakeRequest(method="POST", headers={"Authorization": "Bearer reader-token"})
    response = _FakeResponse()

    context = _run(helper.enforce(request, response))

    assert context.is_authenticated is False
    assert "Warning" in response.headers


def test_enforce_allows_sufficient_role_and_enriches_context() -> None:
    helper = _make_helper(
        True,
        {
            "admin-token": {
                "preferred_username": "working_admin_user",
                "realm_access": {"roles": ["offline_access"]},
                "resource_access": {"account": {"roles": ["manage-account"]}},
                "scope": "profile email",
            }
        },
    )
    request = _FakeRequest(method="DELETE", headers={"Authorization": "Bearer admin-token"})
    response = _FakeResponse()

    context = _run(helper.enforce(request, response))

    assert context.is_authenticated is True
    assert context.effective_role == "admin_role"
    assert context.token_roles == frozenset({"offline_access", "manage-account"})
    assert context.scopes == frozenset({"profile", "email"})
    assert "Warning" not in response.headers
