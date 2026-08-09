from fastapi import FastAPI
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
