import logging
import time
from collections.abc import Generator
from functools import lru_cache
from typing import Any

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.engine import ExceptionContext
from sqlalchemy.orm import Session, sessionmaker

from pilot_api.config.settings import get_settings

logger = logging.getLogger(__name__)

_STARTED_KEY = "pilot_api_database_call_started"
_MAX_STATEMENT_LENGTH = 200


def _summarize(statement: str) -> str:
    # Statements carry bind placeholders, never parameter values, so they are safe to log.
    summary = " ".join(statement.split())
    if len(summary) > _MAX_STATEMENT_LENGTH:
        return f"{summary[:_MAX_STATEMENT_LENGTH]}..."
    return summary


def _elapsed_ms(info: dict[str, Any]) -> float:
    started = info.pop(_STARTED_KEY, None)
    return 0.0 if started is None else (time.perf_counter() - started) * 1000


def _before_cursor_execute(conn, cursor, statement, parameters, context, executemany) -> None:
    conn.info[_STARTED_KEY] = time.perf_counter()
    logger.info("Database call started: %s", _summarize(statement))


def _after_cursor_execute(conn, cursor, statement, parameters, context, executemany) -> None:
    logger.info(
        "Database call completed: %s (%.1f ms)", _summarize(statement), _elapsed_ms(conn.info)
    )


def _handle_error(exception_context: ExceptionContext) -> None:
    connection = exception_context.connection
    elapsed = _elapsed_ms(connection.info) if connection is not None else 0.0
    logger.error(
        "Database call failed: %s (%.1f ms) %s",
        _summarize(exception_context.statement or ""),
        elapsed,
        type(exception_context.original_exception).__name__,
    )


# Registered on the Engine class, not one instance, so every engine (including any built
# by tests) logs the beginning and end of each database call. The request ids and caller
# name are stamped on each line by RequestContextFilter.
event.listen(Engine, "before_cursor_execute", _before_cursor_execute)
event.listen(Engine, "after_cursor_execute", _after_cursor_execute)
event.listen(Engine, "handle_error", _handle_error)


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    return create_engine(
        get_settings().resolved_database_url,
        future=True,
        pool_pre_ping=True,
    )


@lru_cache(maxsize=1)
def get_session_factory() -> sessionmaker[Session]:
    return sessionmaker(bind=get_engine(), autocommit=False, autoflush=False, class_=Session)


def get_db_session() -> Generator[Session, None, None]:
    session = get_session_factory()()
    try:
        yield session
    finally:
        session.close()
