import logging
from http import HTTPStatus

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from pilot_api.dto.schemas import ProblemDetailsDto
from pilot_api.exception.errors import AppError

logger = logging.getLogger(__name__)


def _problem_response(status_code: int, title: str, detail: str, instance: str) -> JSONResponse:
    payload = ProblemDetailsDto(
        type=f"https://httpstatuses.com/{status_code}",
        title=title,
        status=status_code,
        detail=detail,
        instance=instance,
    )
    return JSONResponse(status_code=status_code, content=payload.model_dump(exclude_none=True))


# The shared OpenAPI definition declares 401/403 bodies as a plain JSON string.
_STRING_BODY_STATUSES = {401, 403}


def _error_response(status_code: int, title: str, detail: str, instance: str) -> JSONResponse:
    if status_code in _STRING_BODY_STATUSES:
        return JSONResponse(status_code=status_code, content=detail)
    return _problem_response(status_code, title, detail, instance)


def _validation_detail(exc: RequestValidationError) -> str:
    # Built from loc/msg only: str(exc) would echo the submitted input values.
    return "; ".join(
        f"{'.'.join(str(part) for part in error['loc'])}: {error['msg']}"
        for error in exc.errors()
    )


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
        return _error_response(exc.status_code, exc.title, exc.detail, str(request.url.path))

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return _problem_response(
            400, "Bad Request", _validation_detail(exc), str(request.url.path)
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        try:
            title = HTTPStatus(exc.status_code).phrase
        except ValueError:
            title = "Error"
        return _error_response(exc.status_code, title, str(exc.detail), str(request.url.path))

    @app.exception_handler(Exception)
    async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unexpected error", extra={"operation_id": request.url.path})
        return _problem_response(
            500, "Internal Server Error", "Unexpected server error.", str(request.url.path)
        )
