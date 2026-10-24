import uuid
from contextvars import ContextVar
from dataclasses import dataclass

from starlette.requests import Request
from starlette.responses import Response

CORRELATION_ID_HEADER = "X-Correlation-Id"
REQUEST_ID_HEADER = "X-Request-Id"


@dataclass(frozen=True)
class RequestSettings:
    """Per-request values, created once at the start of a request and shared for its lifetime."""

    request_id: str
    correlation_id: str

    @classmethod
    def from_request(cls, request: Request) -> "RequestSettings":
        # Header lookup is case-insensitive; a missing or blank header gets a fresh GUID.
        correlation_id = request.headers.get(CORRELATION_ID_HEADER) or str(uuid.uuid4())
        return cls(request_id=str(uuid.uuid4()), correlation_id=correlation_id)

    def apply_to(self, response: Response) -> None:
        response.headers[CORRELATION_ID_HEADER] = self.correlation_id
        response.headers[REQUEST_ID_HEADER] = self.request_id


# Set per request by RequestContextMiddleware so code without access to the Request
# (logging filters, services) can still reach the current request's settings.
request_settings_var: ContextVar[RequestSettings | None] = ContextVar(
    "request_settings", default=None
)


def get_current_request_settings() -> RequestSettings | None:
    return request_settings_var.get()
