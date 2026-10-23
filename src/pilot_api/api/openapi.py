from typing import Any

from fastapi import FastAPI

# FastAPI documents a 422 for every operation with parameters, but the
# RequestValidationError handler turns validation failures into 400 ProblemDetails.
_UNUSED_SCHEMAS = ("HTTPValidationError", "ValidationError")


def _align_with_shared_definition(schema: dict[str, Any]) -> None:
    for operations in schema.get("paths", {}).values():
        for operation in operations.values():
            operation.get("responses", {}).pop("422", None)
            content = operation.get("requestBody", {}).get("content", {})
            # FastAPI parses any application/*+json body as JSON, as the definition allows.
            if "application/json" in content:
                content.setdefault("application/*+json", dict(content["application/json"]))

    schemas = schema.get("components", {}).get("schemas", {})
    for name in _UNUSED_SCHEMAS:
        schemas.pop(name, None)


def install_openapi(app: FastAPI) -> None:
    default_openapi = app.openapi

    def openapi() -> dict[str, Any]:
        if app.openapi_schema is None:
            # default_openapi caches its result on app.openapi_schema.
            _align_with_shared_definition(default_openapi())
        return app.openapi_schema

    app.openapi = openapi  # type: ignore[method-assign]
