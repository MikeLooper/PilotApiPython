class AppError(Exception):
    status_code: int = 500
    title: str = "Internal Server Error"

    def __init__(self, detail: str, *, status_code: int | None = None, title: str | None = None):
        super().__init__(detail)
        self.detail = detail
        if status_code is not None:
            self.status_code = status_code
        if title is not None:
            self.title = title


class NotFoundError(AppError):
    status_code = 404
    title = "Not Found"


class ConflictError(AppError):
    status_code = 409
    title = "Conflict"


class BadRequestError(AppError):
    status_code = 400
    title = "Bad Request"


class UnauthorizedError(AppError):
    status_code = 401
    title = "Unauthorized"


class ForbiddenError(AppError):
    status_code = 403
    title = "Forbidden"
