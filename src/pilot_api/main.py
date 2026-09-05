import logging
import uuid
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request, Response
from opentelemetry import trace
from starlette.middleware.base import BaseHTTPMiddleware

from pilot_api.api.router import api_router
from pilot_api.config.logging_config import configure_logging
from pilot_api.config.settings import get_settings
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
        response: Response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Correlation-ID"] = correlation_id
        return response


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging()
    configure_telemetry()

    app = FastAPI(
        title=settings.app_name,
        version=f"Version: {settings.app_version}",
        description=f"Description: {settings.app_description}",
        summary=f"Summary: {settings.app_summary}",
        contact={
            "name": f"Contact: {settings.app_contact_name}",
            "email": settings.app_contact_email,
            "url": settings.app_contact_url,
        },
        license_info={
            "name": f"License: {settings.app_license_name}",
            "url": settings.app_license_url,
        },
        lifespan=lifespan,
    )
    app.add_middleware(RequestContextMiddleware)
    app.include_router(api_router)
    register_exception_handlers(app)
    instrument_app(app)

    logging.getLogger(__name__).info("Application initialized")
    return app


app = create_app()


def run() -> None:
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    run()
