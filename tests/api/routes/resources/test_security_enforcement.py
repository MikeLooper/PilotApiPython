from collections.abc import Callable, Generator
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from pilot_api.api.dependencies import get_session
from pilot_api.config.settings import Settings
from pilot_api.main import app
from pilot_api.security.role_repository import UserRoleRepository
from pilot_api.security.security_helper import SecurityHelper, get_security_helper
from pilot_api.security.token_validator import TokenValidationError

_CATEGORY_PAYLOAD = {
    "categoryID": 1,
    "categoryName": "Beverages",
    "description": "Soft drinks",
    "picture": None,
}


class _FakeTokenValidator:
    """Maps opaque test tokens straight to claims, bypassing real JWT/JWKS."""

    _TOKENS: dict[str, dict[str, Any]] = {
        "reader-token": {"preferred_username": "reader_user"},
        "writer-token": {"preferred_username": "working_user"},
        "admin-token": {"preferred_username": "working_admin_user"},
    }

    def decode(self, raw_token: str) -> dict[str, Any]:
        claims = self._TOKENS.get(raw_token)
        if claims is None:
            raise TokenValidationError("unknown test token")
        return claims


@pytest.fixture
def security_client(db_session: Session) -> Generator[Callable[[bool], TestClient], None, None]:
    def override_get_session() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_session] = override_get_session

    def make(security_active: bool) -> TestClient:
        app.dependency_overrides[get_security_helper] = lambda: SecurityHelper(
            settings=Settings(security_active=security_active),
            token_validator=_FakeTokenValidator(),
            role_repository=UserRoleRepository(),
        )
        return TestClient(app)

    yield make

    app.dependency_overrides.clear()


def test_missing_token_is_blocked_when_active(
    security_client: Callable[[bool], TestClient],
) -> None:
    client = security_client(True)

    response = client.get("/v1/categories/get-all", headers={"ApiVersion": "1"})

    assert response.status_code == 401


def test_reader_can_read_but_not_write(security_client: Callable[[bool], TestClient]) -> None:
    client = security_client(True)
    headers = {"ApiVersion": "1", "Authorization": "Bearer reader-token"}

    assert client.get("/v1/categories/get-all", headers=headers).status_code == 200
    add_response = client.post("/v1/categories/add", json=_CATEGORY_PAYLOAD, headers=headers)
    assert add_response.status_code == 403


def test_writer_can_write_but_not_delete(security_client: Callable[[bool], TestClient]) -> None:
    client = security_client(True)
    headers = {"ApiVersion": "1", "Authorization": "Bearer writer-token"}

    add_response = client.post("/v1/categories/add", json=_CATEGORY_PAYLOAD, headers=headers)
    assert add_response.status_code == 201
    assert client.delete("/v1/categories/delete/1", headers=headers).status_code == 403


def test_admin_can_delete(security_client: Callable[[bool], TestClient]) -> None:
    client = security_client(True)
    headers = {"ApiVersion": "1", "Authorization": "Bearer admin-token"}

    add_response = client.post("/v1/categories/add", json=_CATEGORY_PAYLOAD, headers=headers)
    assert add_response.status_code == 201

    delete_response = client.delete("/v1/categories/delete/1", headers=headers)
    assert delete_response.status_code == 204


def test_inactive_security_allows_unauthenticated_access_with_warning(
    security_client: Callable[[bool], TestClient],
) -> None:
    client = security_client(False)

    response = client.get("/v1/categories/get-all", headers={"ApiVersion": "1"})

    assert response.status_code == 200
    assert "Warning" in response.headers


def test_inactive_security_allows_insufficient_role_with_warning(
    security_client: Callable[[bool], TestClient],
) -> None:
    client = security_client(False)
    headers = {"ApiVersion": "1", "Authorization": "Bearer reader-token"}

    response = client.post("/v1/categories/add", json=_CATEGORY_PAYLOAD, headers=headers)

    assert response.status_code == 201
    assert "Warning" in response.headers
