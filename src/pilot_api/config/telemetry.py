import logging
import traceback

from fastapi import FastAPI
from opentelemetry import metrics, trace
from opentelemetry._logs import set_logger_provider
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.instrumentation.logging.handler import LoggingHandler
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk._logs import LoggerProvider
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import Span, SpanProcessor, TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from pilot_api.config.request_settings import RequestSettings, get_current_request_settings
from pilot_api.config.settings import get_settings

_configured = False

SPAN_CORRELATION_ID_ATTRIBUTE = "correlationId"
SPAN_REQUEST_ID_ATTRIBUTE = "request.Id"
LOG_CORRELATION_ID_ATTRIBUTE = "CorrelationId"
LOG_REQUEST_ID_ATTRIBUTE = "Request.Id"
LOG_EXCEPTION_MESSAGE_ATTRIBUTE = "Exception.Message"
LOG_EXCEPTION_INNER_EXCEPTION_ATTRIBUTE = "Exception.InnerException"


def tag_span_with_request_settings(
    span: trace.Span, request_settings: RequestSettings
) -> None:
    span.set_attribute(SPAN_CORRELATION_ID_ATTRIBUTE, request_settings.correlation_id)
    span.set_attribute(SPAN_REQUEST_ID_ATTRIBUTE, request_settings.request_id)


class RequestSettingsSpanProcessor(SpanProcessor):
    """Tags every span started during a request (e.g. SQLAlchemy queries) with its ids.

    The request span itself starts before RequestContextMiddleware creates the
    RequestSettings, so the middleware tags that one directly.
    """

    def on_start(self, span: Span, parent_context=None) -> None:
        request_settings = get_current_request_settings()
        if request_settings:
            tag_span_with_request_settings(span, request_settings)


class OtelLogEnrichmentFilter(logging.Filter):
    """Adds request ids and exception details to the OTLP log record's attributes.

    LoggingHandler exports every non-reserved LogRecord attribute, so setting them
    here is enough. It already records exception.type, exception.message (from
    args[0], when args exist) and exception.stacktrace (whenever a traceback
    exists, so a stacktrace is never added here); only what it leaves out is added.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        request_settings = get_current_request_settings()
        if request_settings:
            setattr(record, LOG_CORRELATION_ID_ATTRIBUTE, request_settings.correlation_id)
            setattr(record, LOG_REQUEST_ID_ATTRIBUTE, request_settings.request_id)

        exception = record.exc_info[1] if record.exc_info else None
        if exception is None:
            return True
        if not exception.args and str(exception):
            setattr(record, LOG_EXCEPTION_MESSAGE_ATTRIBUTE, str(exception))
        # Python's equivalent of an inner exception: an explicit "raise ... from"
        # cause, else the exception being handled when this one was raised.
        inner_exception = exception.__cause__ or (
            None if exception.__suppress_context__ else exception.__context__
        )
        if inner_exception is not None:
            setattr(
                record,
                LOG_EXCEPTION_INNER_EXCEPTION_ATTRIBUTE,
                "".join(traceback.format_exception(inner_exception)),
            )
        return True


def _build_resource() -> Resource:
    settings = get_settings()
    return Resource.create(
        {
            "service.name": settings.otel_service_name,
            "service.version": settings.app_version,
            "deployment.environment": settings.otel_environment,
        }
    )


def _build_exporters(signal: str):
    settings = get_settings()
    if settings.otel_exporter_otlp_protocol == "http":
        endpoint = f"{settings.otel_exporter_otlp_endpoint}/v1/{signal}"
        if signal == "traces":
            from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

            return OTLPSpanExporter(endpoint=endpoint)
        if signal == "metrics":
            from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter

            return OTLPMetricExporter(endpoint=endpoint)
        from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter

        return OTLPLogExporter(endpoint=endpoint)

    endpoint = settings.otel_exporter_otlp_endpoint
    if signal == "traces":
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

        return OTLPSpanExporter(endpoint=endpoint)
    if signal == "metrics":
        from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter

        return OTLPMetricExporter(endpoint=endpoint)
    from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter

    return OTLPLogExporter(endpoint=endpoint)


def configure_telemetry() -> None:
    """Wires up OTLP export of traces, metrics, and logs to the OTEL collector."""
    global _configured
    settings = get_settings()
    if not settings.otel_enabled or _configured:
        return

    resource = _build_resource()

    tracer_provider = TracerProvider(resource=resource)
    tracer_provider.add_span_processor(RequestSettingsSpanProcessor())
    tracer_provider.add_span_processor(BatchSpanProcessor(_build_exporters("traces")))
    trace.set_tracer_provider(tracer_provider)

    meter_provider = MeterProvider(
        resource=resource,
        metric_readers=[PeriodicExportingMetricReader(_build_exporters("metrics"))],
    )
    metrics.set_meter_provider(meter_provider)

    logger_provider = LoggerProvider(resource=resource)
    logger_provider.add_log_record_processor(BatchLogRecordProcessor(_build_exporters("logs")))
    set_logger_provider(logger_provider)

    # instrument() attaches its own OTLP logging handler to the root logger
    # (reading the logger_provider set above) and injects otelTraceID/otelSpanID
    # onto every LogRecord, so console and OTLP logs alike carry correlation IDs.
    LoggingInstrumentor().instrument(inject_trace_context=True)
    for handler in logging.getLogger().handlers:
        if isinstance(handler, LoggingHandler):
            handler.addFilter(OtelLogEnrichmentFilter())

    from pilot_api.config.database import get_engine

    SQLAlchemyInstrumentor().instrument(engine=get_engine(), tracer_provider=tracer_provider)

    _configured = True


def instrument_app(app: FastAPI) -> None:
    settings = get_settings()
    if not settings.otel_enabled:
        return
    FastAPIInstrumentor.instrument_app(app)
