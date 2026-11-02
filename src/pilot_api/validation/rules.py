from typing import Annotated

from fastapi import Depends, Header


def get_api_version(
    api_version: Annotated[
        str | None,
        Header(
            alias="X-Api-Version",
            description="The version of the API that should be used for the current call.  If "
            "missing, the application default version will be used.",
            examples=["1.2.3"],
            max_length=15,
        ),
    ] = None,
) -> str | None:
    return api_version


# Declared so the header is documented (and its length validated) on each operation;
# RequestSettings.from_request is what actually reads it and makes it available to logging.
def get_caller_name(
    caller_name: Annotated[
        str | None,
        Header(
            alias="X-Caller-Name",
            description="Name of the caller.",
            examples=["PilotAngularUi"],
            max_length=100,
        ),
    ] = None,
) -> str | None:
    return caller_name


# Declared so the header is documented on each operation; RequestSettings.from_request
# is what actually reads it (header names are case-insensitive) and propagates it.
def get_correlation_id(
    correlation_id: Annotated[
        str | None,
        Header(
            alias="X-Correlation-Id",
            description="Unique identifier used for tracing a transaction across microservices.",
            examples=["7ea2c7f7-8b46-475d-86f8-7aaaa9e4a35b"],
            max_length=40,
            json_schema_extra={"format": "uuid"},
        ),
    ] = None,
) -> str | None:
    return correlation_id


# The headers every operation in the shared definition accepts, in its declared order.
COMMON_HEADER_DEPENDENCIES = [
    Depends(get_api_version),
    Depends(get_caller_name),
    Depends(get_correlation_id),
]
