from fastapi.testclient import TestClient


def _operations(schema: dict) -> list[tuple[str, str, dict]]:
    return [
        (path, method, operation)
        for path, operations in schema["paths"].items()
        for method, operation in operations.items()
    ]


def test_no_operation_documents_a_422_response(client: TestClient) -> None:
    schema = client.get("/openapi.json").json()

    for path, method, operation in _operations(schema):
        assert "422" not in operation["responses"], f"{method.upper()} {path}"
    assert "HTTPValidationError" not in schema["components"]["schemas"]
    assert "ValidationError" not in schema["components"]["schemas"]


def test_v1_operations_document_standard_error_responses(client: TestClient) -> None:
    schema = client.get("/openapi.json").json()

    for path, method, operation in _operations(schema):
        if path.startswith("/v1/"):
            assert {"400", "401", "403", "500"} <= set(operation["responses"]), (
                f"{method.upper()} {path}"
            )


def test_system_operations_document_only_ok_and_server_error(client: TestClient) -> None:
    schema = client.get("/openapi.json").json()

    for path in ("/healthcheck", "/about"):
        assert set(schema["paths"][path]["get"]["responses"]) == {"200", "500"}, path


def test_error_responses_reference_problem_details_schemas(client: TestClient) -> None:
    responses = client.get("/openapi.json").json()["paths"]["/v1/categories/add"]["post"][
        "responses"
    ]

    assert responses["400"]["content"]["application/json"]["schema"] == {
        "$ref": "#/components/schemas/ProblemDetailsBadRequestDto"
    }
    assert responses["500"]["content"]["application/json"]["schema"] == {
        "$ref": "#/components/schemas/ProblemDetailsDto"
    }
    assert responses["401"]["content"]["application/json"]["schema"] == {"type": "string"}
    assert responses["403"]["content"]["application/json"]["schema"] == {"type": "string"}


def test_problem_details_requires_type_and_title(client: TestClient) -> None:
    schemas = client.get("/openapi.json").json()["components"]["schemas"]

    for name in ("ProblemDetailsDto", "ProblemDetailsBadRequestDto"):
        assert set(schemas[name]["required"]) == {"type", "title"}, name
        assert schemas[name]["additionalProperties"] is True, name


def test_request_bodies_accept_structured_json_media_type(client: TestClient) -> None:
    schema = client.get("/openapi.json").json()

    for path, method, operation in _operations(schema):
        if "requestBody" in operation:
            content = operation["requestBody"]["content"]
            assert set(content) == {"application/json", "application/*+json"}, (
                f"{method.upper()} {path}"
            )
            assert content["application/*+json"] == content["application/json"]


def test_bearer_security_scheme_matches_definition(client: TestClient) -> None:
    schema = client.get("/openapi.json").json()

    assert schema["components"]["securitySchemes"] == {
        "Bearer": {
            "type": "http",
            "description": "JWT bearer authentication",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    operation = schema["paths"]["/v1/categories/get-all"]["get"]
    assert operation["security"] == [{"Bearer": []}]
