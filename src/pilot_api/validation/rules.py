from typing import Annotated

from fastapi import Header


def get_api_version(
    api_version: Annotated[
        str | None,
        Header(
            alias="X-Api-Version",
            description="The version of the API that should be used for the current call.  If "
            "missing, the application default version will be used.",
            examples=["1.2.3"],
        ),
    ] = None,
) -> str | None:
    return api_version


# Declared so the header is documented on each operation; RequestSettings.from_request
# is what actually reads it (header names are case-insensitive) and propagates it.
def get_correlation_id(
    correlation_id: Annotated[
        str | None,
        Header(
            alias="X-Correlation-Id",
            description="Unique identifier used for tracing a transaction across microservices.",
            examples=["7ea2c7f7-8b46-475d-86f8-7aaaa9e4a35b"],
            json_schema_extra={"format": "uuid"},
        ),
    ] = None,
) -> str | None:
    return correlation_id
