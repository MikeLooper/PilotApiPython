from fastapi.testclient import TestClient

from pilot_api.validation.rules import get_api_version, get_correlation_id


def test_get_api_version_returns_header_value_when_provided() -> None:
    assert get_api_version("1") == "1"


def test_get_api_version_returns_none_when_missing() -> None:
    assert get_api_version(None) is None


def test_get_correlation_id_returns_header_value_when_provided() -> None:
    correlation_id = "7ea2c7f7-8b46-475d-86f8-7aaaa9e4a35b"
    assert get_correlation_id(correlation_id) == correlation_id


def test_get_correlation_id_returns_none_when_missing() -> None:
    assert get_correlation_id(None) is None


def _header_names(operation: dict) -> set[str]:
    return {param["name"] for param in operation.get("parameters", []) if param["in"] == "header"}


def test_version_and_correlation_headers_are_documented_on_every_v1_operation(
    client: TestClient,
) -> None:
    schema = client.get("/openapi.json").json()

    for path, operations in schema["paths"].items():
        if not path.startswith("/v1/"):
            continue
        for method, operation in operations.items():
            assert _header_names(operation) == {"X-Api-Version", "X-Correlation-Id"}, (
                f"{method.upper()} {path}"
            )


def test_system_operations_document_no_headers(client: TestClient) -> None:
    schema = client.get("/openapi.json").json()

    for path in ("/healthcheck", "/about"):
        assert _header_names(schema["paths"][path]["get"]) == set(), path
