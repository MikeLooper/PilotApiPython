from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from pilot_api.exception.errors import BadRequestError
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
