import logging
from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from pilot_api import main
from pilot_api.config.logging_config import (
    RequestContextFilter,
    correlation_id_var,
    request_id_var,
)
from pilot_api.exception.handlers import register_exception_handlers
from pilot_api.main import RequestContextMiddleware, lifespan


def _context_echo_app() -> FastAPI:
    app = FastAPI()
    app.add_middleware(RequestContextMiddleware)

    @app.get("/context")
    def context() -> dict[str, str]:
        return {"request_id": request_id_var.get(), "correlation_id": correlation_id_var.get()}

    return app


def test_middleware_exposes_request_ids_to_handlers_through_context_vars() -> None:
    client = TestClient(_context_echo_app())

    response = client.get(
        "/context", headers={"X-Request-ID": "req-1", "X-Correlation-ID": "corr-1"}
    )

    assert response.json() == {"request_id": "req-1", "correlation_id": "corr-1"}
    assert response.headers["X-Request-ID"] == "req-1"
    assert response.headers["X-Correlation-ID"] == "corr-1"
    assert request_id_var.get() == "-"


def test_middleware_generates_request_id_and_defaults_correlation_id_to_it() -> None:
    client = TestClient(_context_echo_app())

    body = client.get("/context").json()

    assert body["request_id"] != "-"
    assert body["correlation_id"] == body["request_id"]


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
        TestClient(app, raise_server_exceptions=False).get(
            "/boom", headers={"X-Request-ID": "req-err"}
        )
    finally:
        handlers_logger.removeHandler(capture)

    assert [record.request_id for record in records] == ["req-err"]


def test_lifespan_disposes_engine_on_shutdown(monkeypatch: pytest.MonkeyPatch) -> None:
    engine = MagicMock()
    monkeypatch.setattr(main, "get_engine", lambda: engine)
    app = FastAPI(lifespan=lifespan)

    with TestClient(app):
        engine.dispose.assert_not_called()

    engine.dispose.assert_called_once()
