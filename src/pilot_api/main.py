import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request, Response
from opentelemetry import trace
from starlette.middleware.base import BaseHTTPMiddleware

from pilot_api.api.openapi import (
    CONTRACT_INFO,
    OPENAPI_TAGS,
    OPENAPI_VERSION,
    install_openapi,
)
from pilot_api.api.router import api_router
from pilot_api.config.database import get_engine
from pilot_api.config.logging_config import configure_logging
from pilot_api.config.request_settings import RequestSettings, request_settings_var
from pilot_api.config.telemetry import (
    configure_telemetry,
    instrument_app,
    tag_span_with_request_settings,
)
from pilot_api.exception.handlers import register_exception_handlers


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_settings = RequestSettings.from_request(request)
        request.state.request_settings = request_settings
        tag_span_with_request_settings(trace.get_current_span(), request_settings)
        request_settings_token = request_settings_var.set(request_settings)
        # Deliberately not reset when call_next raises: the unhandled-error handler
        # runs outside this middleware and must still log with this request's ids.
        response: Response = await call_next(request)
        request_settings_var.reset(request_settings_token)
        request_settings.apply_to(response)
        return response


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield
    get_engine().dispose()


def create_app() -> FastAPI:
    configure_logging()
    configure_telemetry()

    app = FastAPI(
        **CONTRACT_INFO,
        openapi_tags=OPENAPI_TAGS,
        lifespan=lifespan,
    )
    # Not a constructor argument; FastAPI reads the attribute when building the document.
    app.openapi_version = OPENAPI_VERSION
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
