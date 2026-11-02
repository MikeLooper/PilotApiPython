import pytest
from fastapi.testclient import TestClient

from pilot_api.validation.rules import get_api_version, get_caller_name, get_correlation_id


def test_get_api_version_returns_header_value_when_provided() -> None:
    assert get_api_version("1") == "1"


def test_get_api_version_returns_none_when_missing() -> None:
    assert get_api_version(None) is None


def test_get_caller_name_returns_header_value_when_provided() -> None:
    assert get_caller_name("PilotAngularUi") == "PilotAngularUi"


def test_get_caller_name_returns_none_when_missing() -> None:
    assert get_caller_name(None) is None


def test_get_correlation_id_returns_header_value_when_provided() -> None:
    correlation_id = "7ea2c7f7-8b46-475d-86f8-7aaaa9e4a35b"
    assert get_correlation_id(correlation_id) == correlation_id


def test_get_correlation_id_returns_none_when_missing() -> None:
    assert get_correlation_id(None) is None


def _header_names(operation: dict) -> set[str]:
    return {param["name"] for param in operation.get("parameters", []) if param["in"] == "header"}


def test_common_headers_are_documented_on_every_operation(client: TestClient) -> None:
    schema = client.get("/openapi.json").json()

    for path, operations in schema["paths"].items():
        for method, operation in operations.items():
            assert _header_names(operation) == {
                "X-Api-Version",
                "X-Caller-Name",
                "X-Correlation-Id",
            }, f"{method.upper()} {path}"


_HEADER_MAX_LENGTHS = [("X-Api-Version", 15), ("X-Caller-Name", 100), ("X-Correlation-Id", 40)]


@pytest.mark.parametrize(("header", "max_length"), _HEADER_MAX_LENGTHS)
def test_header_at_max_length_is_accepted(client: TestClient, header: str, max_length: int) -> None:
    response = client.get("/v1/categories/get-all", headers={header: "1" * max_length})

    assert response.status_code == 204


@pytest.mark.parametrize(("header", "max_length"), _HEADER_MAX_LENGTHS)
def test_header_over_max_length_is_a_bad_request(
    client: TestClient, header: str, max_length: int
) -> None:
    response = client.get("/v1/categories/get-all", headers={header: "1" * (max_length + 1)})

    assert response.status_code == 400
    assert response.json()["detail"].startswith(f"header.{header}: ")


@pytest.mark.parametrize(("header", "max_length"), _HEADER_MAX_LENGTHS)
def test_system_header_over_max_length_is_a_bad_request(
    client: TestClient, header: str, max_length: int
) -> None:
    response = client.get("/healthcheck", headers={header: "1" * (max_length + 1)})

    assert response.status_code == 400
