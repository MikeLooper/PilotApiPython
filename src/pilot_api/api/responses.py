from typing import Any

from pilot_api.dto.schemas import ProblemDetailsBadRequestDto, ProblemDetailsDto

# Error responses documented on operations, matching components/responses in the
# shared OpenAPI definition (shared/PilotSharedSource/OpenAPI/PilotApi_v1.yaml).
_STRING_CONTENT = {"application/json": {"schema": {"type": "string"}}}

BAD_REQUEST: dict[int | str, dict[str, Any]] = {
    400: {
        "model": ProblemDetailsBadRequestDto,
        "description": "Bad Request — The server could not understand the request due to "
        "invalid syntax or parameters.",
    }
}
UNAUTHORIZED: dict[int | str, dict[str, Any]] = {
    401: {
        "description": "Unauthorized — Authentication is required or the provided credentials "
        "are invalid or expired.",
        "content": _STRING_CONTENT,
    }
}
FORBIDDEN: dict[int | str, dict[str, Any]] = {
    403: {
        "description": "Forbidden — The authenticated user does not have permission to access "
        "the requested resource.",
        "content": _STRING_CONTENT,
    }
}
INTERNAL_SERVER_ERROR: dict[int | str, dict[str, Any]] = {
    500: {
        "model": ProblemDetailsDto,
        "description": "Internal Server Error — An unexpected error occurred on the server.",
    }
}

SYSTEM_RESPONSES = INTERNAL_SERVER_ERROR
RESOURCE_RESPONSES = BAD_REQUEST | UNAUTHORIZED | FORBIDDEN | INTERNAL_SERVER_ERROR
