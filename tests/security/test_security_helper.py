from collections.abc import Callable, Generator
from types import SimpleNamespace
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from pilot_api.api.dependencies import get_session
from pilot_api.config.settings import Settings
from pilot_api.exception.errors import ForbiddenError, UnauthorizedError
from pilot_api.main import app
from pilot_api.security.role_repository import UserRoleRepository
from pilot_api.security.security_helper import (
    SecurityHelper,
    get_security_helper,
    is_authorized,
)
from pilot_api.security.token_validator import TokenValidationError

READ_METHODS = ["GET", "HEAD", "OPTIONS", "QUERY", "TRACE"]
WRITE_METHODS = ["PATCH", "POST", "PUT"]
ADMIN_METHODS = ["DELETE"]

_CATEGORY_PAYLOAD = {
    "categoryId": 1,
    "categoryName": "Beverages",
    "description": "Soft drinks",
    "picture": None,
}


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
        self.state = SimpleNamespace()


class _FakeResponse:
    def __init__(self) -> None:
        self.headers: dict[str, str] = {}


class _StubTokenValidator:
    """Maps opaque test tokens straight to claims, bypassing real JWT/JWKS."""

    def __init__(self, claims_by_token: dict[str, dict[str, Any]], failure_reason: str = ""):
        self._claims_by_token = claims_by_token
        self._failure_reason = failure_reason or "unknown test token"

    def decode(self, raw_token: str) -> dict[str, Any]:
        claims = self._claims_by_token.get(raw_token)
        if claims is None:
            raise TokenValidationError(self._failure_reason)
        return claims


_APP_TOKENS: dict[str, dict[str, Any]] = {
    "reader-token": {"preferred_username": "reader_user"},
    "writer-token": {"preferred_username": "working_user"},
    "admin-token": {"preferred_username": "working_admin_user"},
}


def _make_helper(
    security_active: bool,
    claims_by_token: dict[str, dict[str, Any]],
    failure_reason: str = "",
) -> SecurityHelper:
    return SecurityHelper(
        settings=Settings(security_active=security_active, app_name="PilotApiPython"),
        token_validator=_StubTokenValidator(claims_by_token, failure_reason),
        role_repository=UserRoleRepository(),
    )


@pytest.mark.parametrize("method", READ_METHODS)
def test_read_only_role_can_read(method: str) -> None:
    assert is_authorized("read_only_role", method) is True


@pytest.mark.parametrize("method", WRITE_METHODS + ADMIN_METHODS)
def test_read_only_role_cannot_write_or_delete(method: str) -> None:
    assert is_authorized("read_only_role", method) is False


@pytest.mark.parametrize("method", READ_METHODS + WRITE_METHODS)
def test_read_write_role_can_read_and_write(method: str) -> None:
    assert is_authorized("read_write_role", method) is True


@pytest.mark.parametrize("method", ADMIN_METHODS)
def test_read_write_role_cannot_delete(method: str) -> None:
    assert is_authorized("read_write_role", method) is False


@pytest.mark.parametrize("method", READ_METHODS + WRITE_METHODS + ADMIN_METHODS)
def test_admin_role_can_do_everything(method: str) -> None:
    assert is_authorized("admin_role", method) is True


@pytest.mark.parametrize("method", READ_METHODS + WRITE_METHODS + ADMIN_METHODS)
def test_unknown_or_missing_role_is_denied_everywhere(method: str) -> None:
    assert is_authorized(None, method) is False
    assert is_authorized("made_up_role", method) is False


def test_enforce_blocks_missing_token_when_active() -> None:
    helper = _make_helper(True, {})

    with pytest.raises(UnauthorizedError):
        helper.enforce(_FakeRequest(), _FakeResponse())


def test_enforce_allows_missing_token_when_inactive_and_sets_warning_header() -> None:
    helper = _make_helper(False, {})
    response = _FakeResponse()

    context = helper.enforce(_FakeRequest(), response)

    assert context.is_authenticated is False
    assert response.headers["Warning"] == '299 PilotApiPython "Missing bearer token."'


def test_enforce_warning_header_is_header_safe() -> None:
    helper = _make_helper(False, {}, failure_reason='bad "segment"\r\nInjected: header')
    request = _FakeRequest(headers={"Authorization": "Bearer junk"})
    response = _FakeResponse()

    helper.enforce(request, response)

    warning = response.headers["Warning"]
    assert "\r" not in warning
    assert "\n" not in warning
    assert warning == (
        "299 PilotApiPython \"Authentication failed: bad 'segment'Injected: header\""
    )


def test_enforce_blocks_insufficient_role_when_active() -> None:
    helper = _make_helper(True, {"reader-token": {"preferred_username": "reader_user"}})
    request = _FakeRequest(method="POST", headers={"Authorization": "Bearer reader-token"})

    with pytest.raises(ForbiddenError):
        helper.enforce(request, _FakeResponse())


def test_enforce_reports_unknown_user_by_id() -> None:
    helper = _make_helper(True, {"stranger-token": {"preferred_username": "stranger"}})
    request = _FakeRequest(headers={"Authorization": "Bearer stranger-token"})

    with pytest.raises(ForbiddenError) as exc_info:
        helper.enforce(request, _FakeResponse())

    assert exc_info.value.detail == "No application role found for user 'stranger'."


def test_enforce_allows_insufficient_role_when_inactive_and_sets_warning_header() -> None:
    helper = _make_helper(False, {"reader-token": {"preferred_username": "reader_user"}})
    request = _FakeRequest(method="POST", headers={"Authorization": "Bearer reader-token"})
    response = _FakeResponse()

    context = helper.enforce(request, response)

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

    context = helper.enforce(request, response)

    assert context.is_authenticated is True
    assert context.effective_role == "admin_role"
    assert context.token_roles == frozenset({"offline_access", "manage-account"})
    assert context.scopes == frozenset({"profile", "email"})
    assert "Warning" not in response.headers


@pytest.fixture
def security_client(db_session: Session) -> Generator[Callable[[bool], TestClient], None, None]:
    def override_get_session() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_session] = override_get_session

    def make(security_active: bool) -> TestClient:
        app.dependency_overrides[get_security_helper] = lambda: _make_helper(
            security_active, _APP_TOKENS
        )
        return TestClient(app)

    yield make

    app.dependency_overrides.clear()


def test_missing_token_is_blocked_when_active(
    security_client: Callable[[bool], TestClient],
) -> None:
    client = security_client(True)

    response = client.get("/v1/categories/get-all", headers={"X-Api-Version": "1"})

    assert response.status_code == 401
    assert response.headers["content-type"] == "application/json"
    assert response.json() == "Missing bearer token."


def test_reader_can_read_but_not_write(security_client: Callable[[bool], TestClient]) -> None:
    client = security_client(True)
    headers = {"X-Api-Version": "1", "Authorization": "Bearer reader-token"}

    assert client.get("/v1/categories/get-all", headers=headers).status_code == 200
    add_response = client.post("/v1/categories/add", json=_CATEGORY_PAYLOAD, headers=headers)
    assert add_response.status_code == 403
    assert add_response.json() == "Role 'read_only_role' is not permitted to perform 'POST'."


def test_writer_can_write_but_not_delete(security_client: Callable[[bool], TestClient]) -> None:
    client = security_client(True)
    headers = {"X-Api-Version": "1", "Authorization": "Bearer writer-token"}

    add_response = client.post("/v1/categories/add", json=_CATEGORY_PAYLOAD, headers=headers)
    assert add_response.status_code == 201
    assert client.delete("/v1/categories/delete/1", headers=headers).status_code == 403


def test_admin_can_delete(security_client: Callable[[bool], TestClient]) -> None:
    client = security_client(True)
    headers = {"X-Api-Version": "1", "Authorization": "Bearer admin-token"}

    add_response = client.post("/v1/categories/add", json=_CATEGORY_PAYLOAD, headers=headers)
    assert add_response.status_code == 201

    delete_response = client.delete("/v1/categories/delete/1", headers=headers)
    assert delete_response.status_code == 204


def test_inactive_security_allows_unauthenticated_access_with_warning(
    security_client: Callable[[bool], TestClient],
) -> None:
    client = security_client(False)

    response = client.get("/v1/categories/get-all", headers={"X-Api-Version": "1"})

    assert response.status_code == 200
    assert "Warning" in response.headers


def test_inactive_security_allows_insufficient_role_with_warning(
    security_client: Callable[[bool], TestClient],
) -> None:
    client = security_client(False)
    headers = {"X-Api-Version": "1", "Authorization": "Bearer reader-token"}

    response = client.post("/v1/categories/add", json=_CATEGORY_PAYLOAD, headers=headers)

    assert response.status_code == 201
    assert "Warning" in response.headers
