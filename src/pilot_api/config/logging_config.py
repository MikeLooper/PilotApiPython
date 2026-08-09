import logging
from logging.config import dictConfig

from pilot_api.config.settings import get_settings


class RequestContextFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, "request_id"):
            record.request_id = "-"
        if not hasattr(record, "correlation_id"):
            record.correlation_id = "-"
        if not hasattr(record, "operation_id"):
            record.operation_id = "-"
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
        "%(request_id)s %(correlation_id)s %(operation_id)s"
    )

    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "filters": {"request_context": {"()": RequestContextFilter}},
            "formatters": {"default": {"()": formatter, "format": format_string}},
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                    "filters": ["request_context"],
                }
            },
            "root": {
                "handlers": ["console"],
                "level": settings.log_level,
            },
        }
    )
