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


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
        return _problem_response(exc.status_code, exc.title, exc.detail, str(request.url.path))

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        return _problem_response(400, "Bad Request", str(exc), str(request.url.path))

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        try:
            title = HTTPStatus(exc.status_code).phrase
        except ValueError:
            title = "Error"
        return _problem_response(exc.status_code, title, str(exc.detail), str(request.url.path))

    @app.exception_handler(Exception)
    async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unexpected error", extra={"operation_id": request.url.path})
        return _problem_response(500, "Internal Server Error", "Unexpected server error.", str(request.url.path))
