import copy
from typing import Any

import pytest
from openapi_comparator import OpenApiComparator, Severity


def _document() -> dict[str, Any]:
    return {
        "openapi": "3.1.1",
        "info": {"title": "Api", "version": "1.0.0"},
        "paths": {
            "/items/get/{itemId}": {
                "get": {
                    "tags": ["Items"],
                    "summary": "Gets an item.",
                    "parameters": [
                        {
                            "name": "itemId",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "integer", "format": "int32"},
                        },
                        {"$ref": "#/components/parameters/TraceHeader"},
                    ],
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/ItemDto"}
                                }
                            },
                        },
                        "400": {"description": "Bad Request"},
                    },
                    "security": [{"Bearer": []}],
                }
            },
            "/items/update": {
                "put": {
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {"schema": {"$ref": "#/components/schemas/ItemDto"}}
                        },
                    },
                    "responses": {
                        "204": {"description": "No Content", "content": {"application/json": {}}}
                    },
                    "security": [{"Bearer": []}],
                }
            },
        },
        "components": {
            "parameters": {
                "TraceHeader": {
                    "name": "X-Trace",
                    "in": "header",
                    "required": False,
                    "schema": {"type": "string", "format": "uuid"},
                }
            },
            "schemas": {
                "ItemDto": {
                    "type": "object",
                    "required": ["name"],
                    "properties": {
                        "itemId": {
                            "type": ["null", "integer", "string"],
                            "pattern": "^-?(?:0|[1-9]\\d*)$",
                            "format": "int32",
                        },
                        "name": {"type": ["null", "string"], "description": "The name."},
                        "owner": {
                            "oneOf": [
                                {"type": "null"},
                                {"$ref": "#/components/schemas/OwnerDto"},
                            ]
                        },
                    },
                },
                "OwnerDto": {"type": "object", "properties": {"ownerName": {"type": "string"}}},
            },
            "securitySchemes": {"Bearer": {"type": "http", "scheme": "bearer"}},
        },
    }


def _findings(expected: dict[str, Any], actual: dict[str, Any]) -> list[tuple[Severity, str]]:
    return [
        (finding.severity, finding.location)
        for finding in OpenApiComparator(expected, actual).compare()
    ]


def _severities_at(findings: list[tuple[Severity, str]], location: str) -> set[Severity]:
    return {severity for severity, finding_location in findings if finding_location == location}


@pytest.fixture
def expected() -> dict[str, Any]:
    return _document()


@pytest.fixture
def actual() -> dict[str, Any]:
    return _document()


def test_compare_identical_documents_no_findings(
    expected: dict[str, Any], actual: dict[str, Any]
) -> None:
    findings = _findings(expected, actual)

    assert findings == []


def test_compare_missing_operation_error(expected: dict[str, Any], actual: dict[str, Any]) -> None:
    del actual["paths"]["/items/update"]

    findings = _findings(expected, actual)

    assert findings == [(Severity.ERROR, "PUT /items/update")]


def test_compare_extra_operation_warn(expected: dict[str, Any], actual: dict[str, Any]) -> None:
    actual["paths"]["/items/delete"] = {"delete": {"responses": {}}}

    findings = _findings(expected, actual)

    assert findings == [(Severity.WARN, "DELETE /items/delete")]


def test_compare_missing_required_parameter_error(
    expected: dict[str, Any], actual: dict[str, Any]
) -> None:
    actual["paths"]["/items/get/{itemId}"]["get"]["parameters"].pop(0)

    findings = _findings(expected, actual)

    assert findings == [(Severity.ERROR, "GET /items/get/{itemId} parameter path:itemId")]


def test_compare_missing_optional_parameter_warn(
    expected: dict[str, Any], actual: dict[str, Any]
) -> None:
    actual["paths"]["/items/get/{itemId}"]["get"]["parameters"].pop(1)

    findings = _findings(expected, actual)

    assert findings == [(Severity.WARN, "GET /items/get/{itemId} parameter header:X-Trace")]


def test_compare_parameter_required_flag_differs_error(
    expected: dict[str, Any], actual: dict[str, Any]
) -> None:
    actual["components"]["parameters"]["TraceHeader"]["required"] = True

    findings = _findings(expected, actual)

    assert findings == [
        (Severity.ERROR, "GET /items/get/{itemId} parameter header:X-Trace required")
    ]


def test_compare_optional_parameter_nullability_info(
    expected: dict[str, Any], actual: dict[str, Any]
) -> None:
    actual["components"]["parameters"]["TraceHeader"]["schema"] = {
        "anyOf": [{"type": "string"}, {"type": "null"}],
        "format": "uuid",
    }

    findings = _findings(expected, actual)

    assert findings == [
        (Severity.INFO, "GET /items/get/{itemId} parameter header:X-Trace schema nullable")
    ]


def test_compare_extra_parameter_warn(expected: dict[str, Any], actual: dict[str, Any]) -> None:
    actual["paths"]["/items/get/{itemId}"]["get"]["parameters"].append(
        {"name": "verbose", "in": "query", "schema": {"type": "boolean"}}
    )

    findings = _findings(expected, actual)

    assert findings == [(Severity.WARN, "GET /items/get/{itemId} parameter query:verbose")]


def test_compare_missing_required_request_body_error(
    expected: dict[str, Any], actual: dict[str, Any]
) -> None:
    del actual["paths"]["/items/update"]["put"]["requestBody"]

    findings = _findings(expected, actual)

    assert findings == [(Severity.ERROR, "PUT /items/update requestBody")]


def test_compare_request_body_media_type_differs_error(
    expected: dict[str, Any], actual: dict[str, Any]
) -> None:
    content = actual["paths"]["/items/update"]["put"]["requestBody"]["content"]
    content["application/xml"] = content.pop("application/json")

    findings = _findings(expected, actual)

    assert _severities_at(findings, "PUT /items/update requestBody application/json") == {
        Severity.ERROR
    }
    assert _severities_at(findings, "PUT /items/update requestBody application/xml") == {
        Severity.ERROR
    }


def test_compare_missing_success_response_error(
    expected: dict[str, Any], actual: dict[str, Any]
) -> None:
    del actual["paths"]["/items/get/{itemId}"]["get"]["responses"]["200"]

    findings = _findings(expected, actual)

    assert (Severity.ERROR, "GET /items/get/{itemId} response 200") in findings


def test_compare_missing_error_response_warn(
    expected: dict[str, Any], actual: dict[str, Any]
) -> None:
    del actual["paths"]["/items/get/{itemId}"]["get"]["responses"]["400"]

    findings = _findings(expected, actual)

    assert findings == [(Severity.WARN, "GET /items/get/{itemId} response 400")]


def test_compare_extra_response_warn(expected: dict[str, Any], actual: dict[str, Any]) -> None:
    actual["paths"]["/items/update"]["put"]["responses"]["409"] = {"description": "Conflict"}

    findings = _findings(expected, actual)

    assert findings == [(Severity.WARN, "PUT /items/update response 409")]


def test_compare_no_content_response_without_schemaless_media_type_info(
    expected: dict[str, Any], actual: dict[str, Any]
) -> None:
    del actual["paths"]["/items/update"]["put"]["responses"]["204"]["content"]

    findings = _findings(expected, actual)

    assert findings == [(Severity.INFO, "PUT /items/update response 204 application/json")]


def test_compare_missing_property_error(expected: dict[str, Any], actual: dict[str, Any]) -> None:
    del actual["components"]["schemas"]["ItemDto"]["properties"]["owner"]

    findings = _findings(expected, actual)

    assert (Severity.ERROR, "components.schemas.ItemDto.owner") in findings


def test_compare_extra_property_warn(expected: dict[str, Any], actual: dict[str, Any]) -> None:
    actual["components"]["schemas"]["ItemDto"]["properties"]["color"] = {"type": "string"}

    findings = _findings(expected, actual)

    assert findings == [(Severity.WARN, "components.schemas.ItemDto.color")]


def test_compare_missing_schema_error(expected: dict[str, Any], actual: dict[str, Any]) -> None:
    expected["components"]["schemas"]["UnusedDto"] = {"type": "object"}

    findings = _findings(expected, actual)

    assert findings == [(Severity.ERROR, "components.schemas.UnusedDto")]


def test_compare_base_type_differs_error(expected: dict[str, Any], actual: dict[str, Any]) -> None:
    actual["components"]["schemas"]["OwnerDto"]["properties"]["ownerName"] = {"type": "integer"}

    findings = _findings(expected, actual)

    assert findings == [(Severity.ERROR, "components.schemas.OwnerDto.ownerName type")]


def test_compare_alternate_types_with_pattern_and_format_info(
    expected: dict[str, Any], actual: dict[str, Any]
) -> None:
    actual["components"]["schemas"]["ItemDto"]["properties"]["itemId"] = {
        "anyOf": [{"type": "integer"}, {"type": "null"}]
    }

    findings = _findings(expected, actual)

    assert {severity for severity, _ in findings} == {Severity.INFO}
    assert len(findings) == 3


@pytest.mark.parametrize(
    ("keyword", "value"),
    [("format", "int64"), ("pattern", "^\\d+$"), ("default", 1), ("enum", [1, 2])],
)
def test_compare_validation_keyword_differs_error(
    expected: dict[str, Any], actual: dict[str, Any], keyword: str, value: Any
) -> None:
    owner_name = expected["components"]["schemas"]["OwnerDto"]["properties"]["ownerName"]
    owner_name[keyword] = copy.deepcopy(value)
    actual["components"]["schemas"]["OwnerDto"]["properties"]["ownerName"][keyword] = (
        "different" if keyword != "enum" else [3]
    )

    findings = _findings(expected, actual)

    assert findings == [(Severity.ERROR, f"components.schemas.OwnerDto.ownerName {keyword}")]


def test_compare_validation_keyword_on_single_type_missing_error(
    expected: dict[str, Any], actual: dict[str, Any]
) -> None:
    del actual["components"]["parameters"]["TraceHeader"]["schema"]["format"]

    findings = _findings(expected, actual)

    assert findings == [
        (Severity.ERROR, "GET /items/get/{itemId} parameter header:X-Trace schema format")
    ]


@pytest.mark.parametrize(
    ("keyword", "value"), [("additionalProperties", False), ("default", "n/a"), ("minLength", 1)]
)
def test_compare_keyword_only_in_implementation_warn(
    expected: dict[str, Any], actual: dict[str, Any], keyword: str, value: Any
) -> None:
    actual["components"]["schemas"]["OwnerDto"]["properties"]["ownerName"][keyword] = value

    findings = _findings(expected, actual)

    assert findings == [(Severity.WARN, f"components.schemas.OwnerDto.ownerName {keyword}")]


def test_compare_required_list_missing_entry_error(
    expected: dict[str, Any], actual: dict[str, Any]
) -> None:
    actual["components"]["schemas"]["ItemDto"]["required"] = []

    findings = _findings(expected, actual)

    assert findings == [(Severity.ERROR, "components.schemas.ItemDto required")]


def test_compare_required_list_extra_entry_warn(
    expected: dict[str, Any], actual: dict[str, Any]
) -> None:
    actual["components"]["schemas"]["ItemDto"]["required"] = ["name", "itemId"]

    findings = _findings(expected, actual)

    assert findings == [(Severity.WARN, "components.schemas.ItemDto required")]


def test_compare_nullability_differs_error(
    expected: dict[str, Any], actual: dict[str, Any]
) -> None:
    actual["components"]["schemas"]["ItemDto"]["properties"]["name"]["type"] = "string"

    findings = _findings(expected, actual)

    assert findings == [(Severity.ERROR, "components.schemas.ItemDto.name nullable")]


def test_compare_nullable_reference_styles_equivalent(
    expected: dict[str, Any], actual: dict[str, Any]
) -> None:
    actual["components"]["schemas"]["ItemDto"]["properties"]["owner"] = {
        "anyOf": [{"$ref": "#/components/schemas/OwnerDto"}, {"type": "null"}]
    }

    findings = _findings(expected, actual)

    assert findings == []


def test_compare_composition_differs_error(
    expected: dict[str, Any], actual: dict[str, Any]
) -> None:
    actual["components"]["schemas"]["OwnerDto"]["properties"]["ownerName"] = {
        "oneOf": [{"type": "string"}, {"type": "integer"}]
    }

    findings = _findings(expected, actual)

    assert (Severity.ERROR, "components.schemas.OwnerDto.ownerName oneOf") in findings


def test_compare_operation_security_differs_error(
    expected: dict[str, Any], actual: dict[str, Any]
) -> None:
    del actual["paths"]["/items/update"]["put"]["security"]

    findings = _findings(expected, actual)

    assert findings == [(Severity.ERROR, "PUT /items/update security")]


def test_compare_security_scheme_differs_error(
    expected: dict[str, Any], actual: dict[str, Any]
) -> None:
    actual["components"]["securitySchemes"]["Bearer"]["scheme"] = "basic"

    findings = _findings(expected, actual)

    assert findings == [(Severity.ERROR, "components.securitySchemes.Bearer")]


@pytest.mark.parametrize("key", ["openapi", "info", "servers", "tags"])
def test_compare_document_metadata_differs_warn(
    expected: dict[str, Any], actual: dict[str, Any], key: str
) -> None:
    actual[key] = "different"

    findings = _findings(expected, actual)

    assert findings == [(Severity.WARN, key)]


def test_compare_operation_id_differs_warn(
    expected: dict[str, Any], actual: dict[str, Any]
) -> None:
    actual["paths"]["/items/update"]["put"]["operationId"] = "update_items"

    findings = _findings(expected, actual)

    assert findings == [(Severity.WARN, "PUT /items/update operationId")]


def test_compare_description_and_summary_differ_info(
    expected: dict[str, Any], actual: dict[str, Any]
) -> None:
    operation = actual["paths"]["/items/get/{itemId}"]["get"]
    operation["summary"] = "Get One"
    operation["responses"]["200"]["description"] = "Successful Response"
    actual["components"]["schemas"]["ItemDto"]["properties"]["name"]["description"] = "Name."

    findings = _findings(expected, actual)

    assert {severity for severity, _ in findings} == {Severity.INFO}
    assert len(findings) == 3


def test_compare_example_differs_info(expected: dict[str, Any], actual: dict[str, Any]) -> None:
    actual["components"]["schemas"]["OwnerDto"]["properties"]["ownerName"]["examples"] = ["Ann"]

    findings = _findings(expected, actual)

    assert findings == [(Severity.INFO, "components.schemas.OwnerDto.ownerName examples")]


def test_compare_component_name_differs_info(
    expected: dict[str, Any], actual: dict[str, Any]
) -> None:
    schemas = actual["components"]["schemas"]
    schemas["OwnerResponseDto"] = schemas.pop("OwnerDto")
    actual["components"]["schemas"]["ItemDto"]["properties"]["owner"]["oneOf"][1] = {
        "$ref": "#/components/schemas/OwnerResponseDto"
    }

    findings = _findings(expected, actual)

    assert findings == [(Severity.INFO, "components.schemas.ItemDto.owner")]


def test_compare_findings_sorted_most_severe_first(
    expected: dict[str, Any], actual: dict[str, Any]
) -> None:
    actual["openapi"] = "3.1.0"
    actual["paths"]["/items/update"]["put"]["summary"] = "Update"
    del actual["paths"]["/items/update"]["put"]["security"]

    findings = _findings(expected, actual)

    assert [severity for severity, _ in findings] == [
        Severity.ERROR,
        Severity.WARN,
        Severity.INFO,
    ]
