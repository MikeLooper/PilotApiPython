import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from pilot_api.exception.errors import BadRequestError, ForbiddenError, UnauthorizedError
from pilot_api.exception.handlers import register_exception_handlers


def test_exception_handler_returns_problem_details_for_app_error() -> None:
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/raise-app-error")
    def raise_app_error() -> None:
        raise BadRequestError("Invalid request")

    client = TestClient(app)

    response = client.get("/raise-app-error")

    assert response.status_code == 400
    body = response.json()
    assert body["title"] == "Bad Request"
    assert body["detail"] == "Invalid request"
    assert body["instance"] == "/raise-app-error"


def test_exception_handler_returns_problem_details_for_validation_error() -> None:
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/validation")
    def validation(value: int) -> dict[str, int]:
        return {"value": value}

    client = TestClient(app)

    response = client.get("/validation?value=not-an-int")

    assert response.status_code == 400
    body = response.json()
    assert body["title"] == "Bad Request"
    assert body["status"] == 400
    assert body["detail"].startswith("query.value: ")
    assert "not-an-int" not in body["detail"]


def test_validation_error_detail_joins_errors_without_echoing_input() -> None:
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/validation")
    def validation(first: int, second: int) -> dict[str, int]:
        return {"first": first, "second": second}

    client = TestClient(app)

    response = client.get("/validation?first=secret-one&second=secret-two")

    detail = response.json()["detail"]
    assert "query.first: " in detail
    assert "; query.second: " in detail
    assert "secret-one" not in detail
    assert "secret-two" not in detail


def test_exception_handler_returns_problem_details_for_http_exception() -> None:
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/raise-http-exception")
    def raise_http_exception() -> None:
        raise HTTPException(status_code=404, detail="Widget not found")

    client = TestClient(app)

    response = client.get("/raise-http-exception")

    assert response.status_code == 404
    body = response.json()
    assert body["title"] == "Not Found"
    assert body["detail"] == "Widget not found"
    assert body["status"] == 404
    assert body["instance"] == "/raise-http-exception"


def test_exception_handler_returns_problem_details_for_unhandled_exception() -> None:
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/raise-unhandled")
    def raise_unhandled() -> None:
        raise ValueError("kaboom")

    client = TestClient(app, raise_server_exceptions=False)

    response = client.get("/raise-unhandled")

    assert response.status_code == 500
    body = response.json()
    assert body["title"] == "Internal Server Error"
    assert body["detail"] == "Unexpected server error."
    assert body["status"] == 500
    assert body["instance"] == "/raise-unhandled"


@pytest.mark.parametrize(
    ("error", "status_code"),
    [(UnauthorizedError("Missing bearer token."), 401), (ForbiddenError("Not allowed."), 403)],
)
def test_exception_handler_returns_string_body_for_auth_app_errors(
    error: Exception, status_code: int
) -> None:
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/raise-auth-error")
    def raise_auth_error() -> None:
        raise error

    response = TestClient(app).get("/raise-auth-error")

    assert response.status_code == status_code
    assert response.headers["content-type"] == "application/json"
    assert response.json() == str(error)


@pytest.mark.parametrize("status_code", [401, 403])
def test_exception_handler_returns_string_body_for_auth_http_exceptions(status_code: int) -> None:
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/raise-auth-http-exception")
    def raise_auth_http_exception() -> None:
        raise HTTPException(status_code=status_code, detail="Denied")

    response = TestClient(app).get("/raise-auth-http-exception")

    assert response.status_code == status_code
    assert response.json() == "Denied"
