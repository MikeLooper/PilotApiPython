from typing import Any

from fastapi import FastAPI

# Document metadata mirrors the shared definition
# (shared/PilotSharedSource/OpenAPI/PilotApi_v1.yaml). It describes the contract, so unlike
# APP_NAME/APP_VERSION it does not change with the deployed build or environment.
OPENAPI_VERSION = "3.1.1"
CONTRACT_INFO: dict[str, Any] = {
    "title": "PilotApi",
    "version": "1.0.0",
    "summary": "Proof of concept API",
    "description": "A proof of concept API to explore best-practices and new ideas.",
    "contact": {
        "name": "Michael Looper",
        "url": "https://github.com/MikeLooper",
        "email": "MikelLooper@gmail.com",
    },
    "license_info": {"name": "MIT", "url": "https://opensource.org"},
}
OPENAPI_TAGS = [
    {"name": name}
    for name in (
        "System",
        "Categories",
        "Customers",
        "Employees",
        "OrderDetails",
        "Orders",
        "Products",
        "Shippers",
        "Suppliers",
    )
]

# FastAPI documents a 422 for every operation with parameters, but the
# RequestValidationError handler turns validation failures into 400 ProblemDetails.
_UNUSED_SCHEMAS = ("HTTPValidationError", "ValidationError")


def _align_with_shared_definition(schema: dict[str, Any]) -> None:
    # FastAPI validates the license URL as a pydantic URL, which appends a trailing "/".
    schema["info"]["license"] = dict(CONTRACT_INFO["license_info"])

    for operations in schema.get("paths", {}).values():
        for operation in operations.values():
            # FastAPI always generates an operationId; the definition declares none.
            operation.pop("operationId", None)
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
