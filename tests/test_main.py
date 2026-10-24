import logging
from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from pilot_api import main
from pilot_api.api.dependencies import RequestSettingsDep
from pilot_api.config.logging_config import RequestContextFilter
from pilot_api.config.request_settings import get_current_request_settings
from pilot_api.exception.handlers import register_exception_handlers
from pilot_api.main import RequestContextMiddleware, lifespan


def _context_echo_app() -> FastAPI:
    app = FastAPI()
    app.add_middleware(RequestContextMiddleware)

    @app.get("/context")
    def context(request_settings: RequestSettingsDep) -> dict[str, str]:
        current = get_current_request_settings()
        return {
            "request_id": request_settings.request_id,
            "correlation_id": request_settings.correlation_id,
            "current_request_id": current.request_id if current else "-",
        }

    return app


def test_middleware_exposes_request_settings_to_handlers() -> None:
    client = TestClient(_context_echo_app())

    response = client.get("/context", headers={"X-Correlation-Id": "corr-1"})

    body = response.json()
    assert body["correlation_id"] == "corr-1"
    assert body["current_request_id"] == body["request_id"]
    assert get_current_request_settings() is None


def test_middleware_writes_request_settings_to_response_headers() -> None:
    client = TestClient(_context_echo_app())

    response = client.get("/context", headers={"X-Correlation-Id": "corr-1"})

    body = response.json()
    assert response.headers["X-Correlation-Id"] == "corr-1"
    assert response.headers["X-Request-Id"] == body["request_id"]


def test_middleware_generates_correlation_id_when_header_missing() -> None:
    client = TestClient(_context_echo_app())

    response = client.get("/context")

    body = response.json()
    assert body["correlation_id"] not in ("-", "", body["request_id"])
    assert response.headers["X-Correlation-Id"] == body["correlation_id"]


def test_unhandled_error_log_carries_request_ids() -> None:
    records: list[logging.LogRecord] = []
    capture = logging.Handler()
    capture.emit = records.append
    capture.addFilter(RequestContextFilter())
    handlers_logger = logging.getLogger("pilot_api.exception.handlers")
    handlers_logger.addHandler(capture)

    app = _context_echo_app()
    register_exception_handlers(app)

    @app.get("/boom")
    def boom() -> None:
        raise RuntimeError("boom")

    try:
        response = TestClient(app, raise_server_exceptions=False).get(
            "/boom", headers={"X-Correlation-Id": "corr-err"}
        )
    finally:
        handlers_logger.removeHandler(capture)

    assert [record.correlation_id for record in records] == ["corr-err"]
    assert [record.request_id for record in records] == [response.headers["X-Request-Id"]]


def test_unhandled_error_response_carries_request_settings_headers() -> None:
    app = _context_echo_app()
    register_exception_handlers(app)

    @app.get("/boom")
    def boom() -> None:
        raise RuntimeError("boom")

    response = TestClient(app, raise_server_exceptions=False).get(
        "/boom", headers={"X-Correlation-Id": "corr-err"}
    )

    assert response.status_code == 500
    assert response.headers["X-Correlation-Id"] == "corr-err"
    assert response.headers["X-Request-Id"] != ""


@pytest.mark.parametrize(("path", "status_code"), [("/not-found", 404), ("/boom", 500)])
def test_problem_details_carry_request_settings_extensions(path: str, status_code: int) -> None:
    app = _context_echo_app()
    register_exception_handlers(app)

    @app.get("/not-found")
    def not_found() -> None:
        raise HTTPException(status_code=404, detail="Widget not found")

    @app.get("/boom")
    def boom() -> None:
        raise RuntimeError("boom")

    response = TestClient(app, raise_server_exceptions=False).get(
        path, headers={"X-Correlation-Id": "corr-err"}
    )

    assert response.status_code == status_code
    body = response.json()
    assert body["correlationId"] == "corr-err"
    assert body["requestId"] == response.headers["X-Request-Id"]
    assert body["timestamp"].endswith("Z")


def test_lifespan_disposes_engine_on_shutdown(monkeypatch: pytest.MonkeyPatch) -> None:
    engine = MagicMock()
    monkeypatch.setattr(main, "get_engine", lambda: engine)
    app = FastAPI(lifespan=lifespan)

    with TestClient(app):
        engine.dispose.assert_not_called()

    engine.dispose.assert_called_once()
