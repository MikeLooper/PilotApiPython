import logging
import uuid
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request, Response
from opentelemetry import trace
from starlette.middleware.base import BaseHTTPMiddleware

from pilot_api.api.openapi import install_openapi
from pilot_api.api.router import api_router
from pilot_api.config.database import get_engine
from pilot_api.config.logging_config import (
    configure_logging,
    correlation_id_var,
    request_id_var,
)
from pilot_api.config.settings import Settings, get_settings
from pilot_api.config.telemetry import configure_telemetry, instrument_app
from pilot_api.exception.handlers import register_exception_handlers


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        correlation_id = request.headers.get("X-Correlation-ID", request_id)
        request.state.request_id = request_id
        request.state.correlation_id = correlation_id
        current_span = trace.get_current_span()
        current_span.set_attribute("app.request_id", request_id)
        current_span.set_attribute("app.correlation_id", correlation_id)
        request_id_token = request_id_var.set(request_id)
        correlation_id_token = correlation_id_var.set(correlation_id)
        # Deliberately not reset when call_next raises: the unhandled-error handler
        # runs outside this middleware and must still log with this request's ids.
        response: Response = await call_next(request)
        request_id_var.reset(request_id_token)
        correlation_id_var.reset(correlation_id_token)
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Correlation-ID"] = correlation_id
        return response


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield
    get_engine().dispose()


def _contact_info(settings: Settings) -> dict[str, str]:
    contact = {
        "name": settings.app_contact_name,
        "email": settings.app_contact_email,
        "url": settings.app_contact_url,
    }
    return {key: value for key, value in contact.items() if value is not None}


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging()
    configure_telemetry()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=settings.app_description,
        summary=settings.app_summary,
        contact=_contact_info(settings) or None,
        license_info={
            "name": settings.app_license_name,
            "url": settings.app_license_url,
        },
        lifespan=lifespan,
    )
    app.add_middleware(RequestContextMiddleware)
    app.include_router(api_router)
    register_exception_handlers(app)
    install_openapi(app)
    instrument_app(app)

    logging.getLogger(__name__).info("Application initialized")
    return app


app = create_app()


def run() -> None:
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    run()
