import logging
import sys

from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from pilot_api.config.request_settings import RequestSettings, request_settings_var
from pilot_api.config.telemetry import (
    OtelLogEnrichmentFilter,
    RequestSettingsSpanProcessor,
    tag_span_with_request_settings,
)

_REQUEST_SETTINGS = RequestSettings(request_id="req-123", correlation_id="corr-456")


def _tracer_with_exporter() -> tuple:
    exporter = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(RequestSettingsSpanProcessor())
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    return provider.get_tracer("test"), exporter


def test_tag_span_sets_correlation_and_request_id_attributes() -> None:
    tracer, exporter = _tracer_with_exporter()

    with tracer.start_as_current_span("request") as span:
        tag_span_with_request_settings(span, _REQUEST_SETTINGS)

    attributes = exporter.get_finished_spans()[0].attributes
    assert attributes["correlationId"] == "corr-456"
    assert attributes["request.Id"] == "req-123"


def test_span_processor_tags_spans_started_during_a_request() -> None:
    tracer, exporter = _tracer_with_exporter()

    token = request_settings_var.set(_REQUEST_SETTINGS)
    try:
        with tracer.start_as_current_span("query"):
            pass
    finally:
        request_settings_var.reset(token)

    attributes = exporter.get_finished_spans()[0].attributes
    assert attributes["correlationId"] == "corr-456"
    assert attributes["request.Id"] == "req-123"


def test_span_processor_leaves_spans_outside_a_request_untagged() -> None:
    tracer, exporter = _tracer_with_exporter()

    with tracer.start_as_current_span("startup"):
        pass

    attributes = exporter.get_finished_spans()[0].attributes
    assert "correlationId" not in attributes
    assert "request.Id" not in attributes


def _enriched_record(exception: BaseException | None = None) -> logging.LogRecord:
    exc_info = (type(exception), exception, exception.__traceback__) if exception else None
    record = logging.LogRecord("test", logging.ERROR, __file__, 1, "msg", (), exc_info)
    OtelLogEnrichmentFilter().filter(record)
    return record


def _raised(exception: BaseException) -> BaseException:
    try:
        raise exception
    except BaseException as caught:
        return caught


def test_log_filter_adds_request_ids_during_a_request() -> None:
    token = request_settings_var.set(_REQUEST_SETTINGS)
    try:
        record = _enriched_record()
    finally:
        request_settings_var.reset(token)

    assert getattr(record, "CorrelationId") == "corr-456"
    assert getattr(record, "Request.Id") == "req-123"


def test_log_filter_adds_nothing_outside_a_request_without_exception() -> None:
    record = _enriched_record()

    for name in ("CorrelationId", "Request.Id", "Exception.Message", "Exception.InnerException"):
        assert not hasattr(record, name)


def test_log_filter_skips_message_already_recorded_from_args() -> None:
    record = _enriched_record(_raised(ValueError("bad value")))

    assert not hasattr(record, "Exception.Message")
    assert not hasattr(record, "Exception.InnerException")


def test_log_filter_adds_message_when_exception_has_no_args() -> None:
    class CustomError(Exception):
        def __str__(self) -> str:
            return "custom message"

    record = _enriched_record(_raised(CustomError()))

    assert getattr(record, "Exception.Message") == "custom message"


def test_log_filter_skips_unavailable_message() -> None:
    record = _enriched_record(_raised(ValueError()))

    assert not hasattr(record, "Exception.Message")


def test_log_filter_adds_explicit_cause_as_inner_exception() -> None:
    try:
        try:
            raise KeyError("missing")
        except KeyError as inner:
            raise RuntimeError("outer") from inner
    except RuntimeError:
        record = _enriched_record(sys.exc_info()[1])

    inner_exception = getattr(record, "Exception.InnerException")
    assert "KeyError: 'missing'" in inner_exception
    assert "RuntimeError" not in inner_exception


def test_log_filter_adds_implicit_context_as_inner_exception() -> None:
    try:
        try:
            raise KeyError("missing")
        except KeyError:
            raise RuntimeError("outer")
    except RuntimeError:
        record = _enriched_record(sys.exc_info()[1])

    assert "KeyError: 'missing'" in getattr(record, "Exception.InnerException")


def test_log_filter_skips_suppressed_context() -> None:
    try:
        try:
            raise KeyError("missing")
        except KeyError:
            raise RuntimeError("outer") from None
    except RuntimeError:
        record = _enriched_record(sys.exc_info()[1])

    assert not hasattr(record, "Exception.InnerException")
