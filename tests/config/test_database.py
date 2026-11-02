import logging
from collections.abc import Generator

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

from pilot_api.config import database
from pilot_api.config.logging_config import RequestContextFilter
from pilot_api.config.request_settings import RequestSettings, request_settings_var

_REQUEST_SETTINGS = RequestSettings(
    request_id="req-123", correlation_id="corr-456", caller_name="PilotAngularUi"
)


@pytest.fixture
def database_records() -> Generator[list[logging.LogRecord], None, None]:
    records: list[logging.LogRecord] = []
    capture = logging.Handler()
    capture.emit = records.append
    capture.addFilter(RequestContextFilter())
    database_logger = logging.getLogger(database.__name__)
    previous_level = database_logger.level
    database_logger.setLevel(logging.INFO)
    database_logger.addHandler(capture)
    try:
        yield records
    finally:
        database_logger.removeHandler(capture)
        database_logger.setLevel(previous_level)


def _messages(records: list[logging.LogRecord]) -> list[str]:
    return [record.getMessage() for record in records]


def test_database_call_logs_start_and_completion(
    database_records: list[logging.LogRecord],
) -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")

    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    messages = _messages(database_records)
    assert messages[0] == "Database call started: SELECT 1"
    assert messages[1].startswith("Database call completed: SELECT 1 (")


def test_database_call_logs_carry_request_settings(
    database_records: list[logging.LogRecord],
) -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")

    token = request_settings_var.set(_REQUEST_SETTINGS)
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    finally:
        request_settings_var.reset(token)

    assert database_records
    for record in database_records:
        assert record.request_id == "req-123"
        assert record.correlation_id == "corr-456"
        assert record.caller_name == "PilotAngularUi"


def test_failed_database_call_logs_failure(database_records: list[logging.LogRecord]) -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")

    with engine.connect() as connection, pytest.raises(OperationalError):
        connection.execute(text("SELECT * FROM missing_table"))

    messages = _messages(database_records)
    assert messages[0] == "Database call started: SELECT * FROM missing_table"
    assert messages[-1].startswith("Database call failed: SELECT * FROM missing_table (")
    assert messages[-1].endswith("OperationalError")
    assert database_records[-1].levelno == logging.ERROR


def test_summarize_collapses_whitespace() -> None:
    assert database._summarize("SELECT a,\n       b\nFROM t") == "SELECT a, b FROM t"


def test_summarize_truncates_long_statements() -> None:
    summary = database._summarize("SELECT " + "x" * 500)

    assert len(summary) == 203
    assert summary.endswith("...")
