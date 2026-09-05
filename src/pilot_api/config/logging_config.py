import logging
import re
from logging.config import dictConfig

from pilot_api.config.settings import get_settings

_SECRET_PATTERN = re.compile(
    r"(?i)(password|pwd)(\s*[=:]\s*)([^\s&\"']+)"
)
_BASIC_AUTH_PATTERN = re.compile(r"(?i)(Authorization:\s*Basic\s+)([A-Za-z0-9+/=]+)")


def _redact(text: str) -> str:
    text = _SECRET_PATTERN.sub(r"\1\2[REDACTED]", text)
    text = _BASIC_AUTH_PATTERN.sub(r"\1[REDACTED]", text)
    return text


class RequestContextFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, "request_id"):
            record.request_id = "-"
        if not hasattr(record, "correlation_id"):
            record.correlation_id = "-"
        if not hasattr(record, "operation_id"):
            record.operation_id = "-"
        # Populated by LoggingInstrumentor when OTEL_ENABLED=true; default to
        # "0" (OTEL's own convention for "no active span") otherwise, since
        # the format string below always references these fields.
        if not hasattr(record, "otelTraceID"):
            record.otelTraceID = "0"
        if not hasattr(record, "otelSpanID"):
            record.otelSpanID = "0"
        return True


class SensitiveDataFilter(logging.Filter):
    """Redacts password-like values from any log entry, wherever they appear."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.msg = _redact(str(record.msg))
        if isinstance(record.args, tuple):
            record.args = tuple(
                _redact(arg) if isinstance(arg, str) else arg for arg in record.args
            )
        return True


def configure_logging() -> None:
    settings = get_settings()
    formatter = (
        "pythonjsonlogger.jsonlogger.JsonFormatter"
        if settings.log_json
        else "logging.Formatter"
    )
    format_string = (
        "%(asctime)s %(levelname)s %(name)s %(message)s "
        "%(request_id)s %(correlation_id)s %(operation_id)s "
        "%(otelTraceID)s %(otelSpanID)s"
    )

    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "filters": {
                "request_context": {"()": RequestContextFilter},
                "sensitive_data": {"()": SensitiveDataFilter},
            },
            "formatters": {"default": {"()": formatter, "format": format_string}},
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                    "filters": ["sensitive_data", "request_context"],
                }
            },
            "root": {
                "handlers": ["console"],
                "level": settings.log_level,
            },
        }
    )
