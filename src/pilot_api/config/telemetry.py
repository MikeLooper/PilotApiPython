from fastapi import FastAPI
from opentelemetry import metrics, trace
from opentelemetry._logs import set_logger_provider
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk._logs import LoggerProvider
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from pilot_api.config.settings import get_settings

_configured = False


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

    from pilot_api.config.database import engine

    SQLAlchemyInstrumentor().instrument(engine=engine, tracer_provider=tracer_provider)

    _configured = True


def instrument_app(app: FastAPI) -> None:
    settings = get_settings()
    if not settings.otel_enabled:
        return
    FastAPIInstrumentor.instrument_app(app)
