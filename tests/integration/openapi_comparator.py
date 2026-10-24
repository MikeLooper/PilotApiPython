"""Compares a reference OpenAPI document against an implemented one.

Each difference is reported as a Finding with a severity:

- ERROR: the implementation breaks the contract (missing operations, schemas or
  properties, required-ness, types, media types, security and validation keywords).
- WARN: the implementation adds to the contract, omits an optional part of it, or
  differs in document metadata.
- INFO: the difference is cosmetic (descriptions, examples, alternate types and
  component names).
"""

from dataclasses import dataclass
from enum import IntEnum
from typing import Any

HTTP_METHODS = ("get", "put", "post", "delete", "options", "head", "patch", "trace")

# Keywords that only document a schema; differences are reported as INFO.
_ANNOTATION_KEYWORDS = ("title", "description", "example", "examples")

# Keywords whose values must match exactly; differences are reported as ERROR.
_VALIDATION_KEYWORDS = (
    "format",
    "pattern",
    "default",
    "enum",
    "const",
    "minimum",
    "maximum",
    "exclusiveMinimum",
    "exclusiveMaximum",
    "minLength",
    "maxLength",
    "minItems",
    "maxItems",
    "uniqueItems",
    "additionalProperties",
)

_COMPOSITION_KEYWORDS = ("oneOf", "anyOf", "allOf")

_METADATA_KEYS = ("openapi", "info", "servers", "tags")


class Severity(IntEnum):
    INFO = 1
    WARN = 2
    ERROR = 3


@dataclass(frozen=True)
class Finding:
    severity: Severity
    location: str
    message: str

    def __str__(self) -> str:
        return f"[{self.severity.name}] {self.location}: {self.message}"


class OpenApiComparator:
    def __init__(self, expected: dict[str, Any], actual: dict[str, Any]) -> None:
        self._expected = expected
        self._actual = actual
        self._findings: list[Finding] = []
        # Component schema pairs already compared, keyed by (expected name, actual name).
        self._compared_components: set[tuple[str, str]] = set()

    def compare(self) -> list[Finding]:
        self._findings = []
        self._compared_components = set()
        self._compare_metadata()
        self._compare_security_schemes()
        self._compare_paths()
        self._compare_unreferenced_components()
        return sorted(self._findings, key=lambda finding: -finding.severity)

    def _add(self, severity: Severity, location: str, message: str) -> None:
        self._findings.append(Finding(severity, location, message))

    # ----- Document level -------------------------------------------------------------

    def _compare_metadata(self) -> None:
        for key in _METADATA_KEYS:
            expected_value = self._expected.get(key)
            actual_value = self._actual.get(key)
            if expected_value != actual_value:
                self._add(
                    Severity.WARN,
                    key,
                    f"expected {expected_value!r}, found {actual_value!r}",
                )

    def _compare_security_schemes(self) -> None:
        expected_schemes = self._expected.get("components", {}).get("securitySchemes", {})
        actual_schemes = self._actual.get("components", {}).get("securitySchemes", {})
        for name in sorted(expected_schemes.keys() | actual_schemes.keys()):
            location = f"components.securitySchemes.{name}"
            if name not in actual_schemes:
                self._add(Severity.ERROR, location, "security scheme is not implemented")
                continue
            if name not in expected_schemes:
                self._add(Severity.ERROR, location, "security scheme is not in the specification")
                continue
            expected_scheme = dict(expected_schemes[name])
            actual_scheme = dict(actual_schemes[name])
            self._compare_description(location, expected_scheme, actual_scheme)
            expected_scheme.pop("description", None)
            actual_scheme.pop("description", None)
            if expected_scheme != actual_scheme:
                self._add(
                    Severity.ERROR,
                    location,
                    f"expected {expected_scheme!r}, found {actual_scheme!r}",
                )

    # ----- Operations -----------------------------------------------------------------

    def _compare_paths(self) -> None:
        expected_operations = _operations(self._expected)
        actual_operations = _operations(self._actual)
        for key in sorted(expected_operations.keys() - actual_operations.keys()):
            self._add(Severity.ERROR, _operation_location(key), "operation is not implemented")
        for key in sorted(actual_operations.keys() - expected_operations.keys()):
            self._add(
                Severity.WARN, _operation_location(key), "operation is not in the specification"
            )
        for key in sorted(expected_operations.keys() & actual_operations.keys()):
            self._compare_operation(
                _operation_location(key), expected_operations[key], actual_operations[key]
            )

    def _compare_operation(
        self, location: str, expected: dict[str, Any], actual: dict[str, Any]
    ) -> None:
        if expected.get("operationId") != actual.get("operationId"):
            self._add(
                Severity.WARN,
                f"{location} operationId",
                f"expected {expected.get('operationId')!r}, found {actual.get('operationId')!r}",
            )
        if sorted(expected.get("tags", [])) != sorted(actual.get("tags", [])):
            self._add(
                Severity.WARN,
                f"{location} tags",
                f"expected {expected.get('tags')!r}, found {actual.get('tags')!r}",
            )
        for key in ("summary", "description"):
            if expected.get(key) != actual.get(key):
                self._add(
                    Severity.INFO,
                    f"{location} {key}",
                    f"expected {expected.get(key)!r}, found {actual.get(key)!r}",
                )
        self._compare_operation_security(location, expected, actual)
        self._compare_parameters(location, expected, actual)
        self._compare_request_body(location, expected, actual)
        self._compare_responses(location, expected, actual)

    def _compare_operation_security(
        self, location: str, expected: dict[str, Any], actual: dict[str, Any]
    ) -> None:
        expected_security = expected.get("security", self._expected.get("security", []))
        actual_security = actual.get("security", self._actual.get("security", []))
        if _normalize_security(expected_security) != _normalize_security(actual_security):
            self._add(
                Severity.ERROR,
                f"{location} security",
                f"expected {expected_security!r}, found {actual_security!r}",
            )

    def _compare_parameters(
        self, location: str, expected: dict[str, Any], actual: dict[str, Any]
    ) -> None:
        expected_parameters = self._parameters(self._expected, expected)
        actual_parameters = self._parameters(self._actual, actual)
        for key in sorted(expected_parameters.keys() | actual_parameters.keys()):
            parameter_location = f"{location} parameter {key[1]}:{key[0]}"
            expected_parameter = expected_parameters.get(key)
            actual_parameter = actual_parameters.get(key)
            if actual_parameter is None:
                required = expected_parameter.get("required", False)
                self._add(
                    Severity.ERROR if required else Severity.WARN,
                    parameter_location,
                    f"{'required' if required else 'optional'} parameter is not implemented",
                )
                continue
            if expected_parameter is None:
                self._add(
                    Severity.WARN, parameter_location, "parameter is not in the specification"
                )
                continue
            self._compare_required_flag(parameter_location, expected_parameter, actual_parameter)
            self._compare_description(parameter_location, expected_parameter, actual_parameter)
            self._compare_schema(
                f"{parameter_location} schema",
                expected_parameter.get("schema", {}),
                actual_parameter.get("schema", {}),
                # An omitted optional parameter and a null one mean the same on the wire.
                nullable_severity=(
                    Severity.ERROR if expected_parameter.get("required") else Severity.INFO
                ),
            )

    def _compare_request_body(
        self, location: str, expected: dict[str, Any], actual: dict[str, Any]
    ) -> None:
        body_location = f"{location} requestBody"
        expected_body = _resolve(self._expected, expected.get("requestBody"))
        actual_body = _resolve(self._actual, actual.get("requestBody"))
        if expected_body is None and actual_body is None:
            return
        if actual_body is None:
            required = expected_body.get("required", False)
            self._add(
                Severity.ERROR if required else Severity.WARN,
                body_location,
                f"{'required' if required else 'optional'} request body is not implemented",
            )
            return
        if expected_body is None:
            self._add(Severity.WARN, body_location, "request body is not in the specification")
            return
        self._compare_required_flag(body_location, expected_body, actual_body)
        self._compare_description(body_location, expected_body, actual_body)
        self._compare_content(body_location, expected_body, actual_body)

    def _compare_responses(
        self, location: str, expected: dict[str, Any], actual: dict[str, Any]
    ) -> None:
        expected_responses = expected.get("responses", {})
        actual_responses = actual.get("responses", {})
        for status in sorted(expected_responses.keys() | actual_responses.keys()):
            response_location = f"{location} response {status}"
            if status not in actual_responses:
                self._add(
                    Severity.ERROR if status.startswith("2") else Severity.WARN,
                    response_location,
                    "response is not implemented",
                )
                continue
            if status not in expected_responses:
                self._add(Severity.WARN, response_location, "response is not in the specification")
                continue
            expected_response = _resolve(self._expected, expected_responses[status])
            actual_response = _resolve(self._actual, actual_responses[status])
            self._compare_description(response_location, expected_response, actual_response)
            self._compare_content(
                response_location,
                expected_response,
                actual_response,
                # A 204 has no body, so a media type without a schema documents nothing.
                schemaless_media_severity=Severity.INFO if status == "204" else Severity.ERROR,
            )

    def _compare_content(
        self,
        location: str,
        expected: dict[str, Any],
        actual: dict[str, Any],
        schemaless_media_severity: Severity = Severity.ERROR,
    ) -> None:
        expected_content = expected.get("content", {})
        actual_content = actual.get("content", {})
        for media_type in sorted(expected_content.keys() | actual_content.keys()):
            media_location = f"{location} {media_type}"
            if media_type not in actual_content:
                schemaless = "schema" not in (expected_content[media_type] or {})
                self._add(
                    schemaless_media_severity if schemaless else Severity.ERROR,
                    media_location,
                    "media type is not implemented",
                )
                continue
            if media_type not in expected_content:
                schemaless = "schema" not in (actual_content[media_type] or {})
                self._add(
                    schemaless_media_severity if schemaless else Severity.ERROR,
                    media_location,
                    "media type is not in the specification",
                )
                continue
            expected_media = expected_content[media_type] or {}
            actual_media = actual_content[media_type] or {}
            for key in ("example", "examples"):
                if expected_media.get(key) != actual_media.get(key):
                    self._add(Severity.INFO, f"{media_location} {key}", "examples differ")
            if "schema" not in expected_media and "schema" not in actual_media:
                continue
            if "schema" not in actual_media:
                self._add(Severity.ERROR, f"{media_location} schema", "schema is not implemented")
                continue
            self._compare_schema(
                f"{media_location} schema", expected_media.get("schema", {}), actual_media["schema"]
            )

    def _compare_required_flag(
        self, location: str, expected: dict[str, Any], actual: dict[str, Any]
    ) -> None:
        expected_required = expected.get("required", False)
        actual_required = actual.get("required", False)
        if expected_required != actual_required:
            self._add(
                Severity.ERROR,
                f"{location} required",
                f"expected {expected_required}, found {actual_required}",
            )

    def _compare_description(
        self, location: str, expected: dict[str, Any], actual: dict[str, Any]
    ) -> None:
        if expected.get("description") != actual.get("description"):
            self._add(
                Severity.INFO,
                f"{location} description",
                f"expected {expected.get('description')!r}, found {actual.get('description')!r}",
            )

    def _parameters(
        self, document: dict[str, Any], operation: dict[str, Any]
    ) -> dict[tuple[str, str], dict[str, Any]]:
        parameters = {}
        for parameter in operation.get("parameters", []):
            resolved = _resolve(document, parameter)
            parameters[(resolved["name"], resolved["in"])] = resolved
        return parameters

    # ----- Schemas --------------------------------------------------------------------

    def _compare_schema(
        self,
        location: str,
        expected: Any,
        actual: Any,
        nullable_severity: Severity = Severity.ERROR,
    ) -> None:
        expected, expected_wrapped_null = _unwrap_nullable_reference(self._expected, expected)
        actual, actual_wrapped_null = _unwrap_nullable_reference(self._actual, actual)
        expected_name = _component_name(expected)
        actual_name = _component_name(actual)
        if expected_name or actual_name:
            if expected_name != actual_name:
                self._add(
                    Severity.INFO,
                    location,
                    f"component name differs: expected {expected_name!r}, found {actual_name!r}",
                )

        expected_schema = _normalize(self._expected, expected)
        actual_schema = _normalize(self._actual, actual)
        expected_nullable = expected_wrapped_null or expected_schema["nullable"]
        actual_nullable = actual_wrapped_null or actual_schema["nullable"]
        if expected_nullable != actual_nullable:
            self._add(
                nullable_severity,
                f"{location} nullable",
                f"expected {expected_nullable}, found {actual_nullable}",
            )

        if expected_name and actual_name:
            pair = (expected_name, actual_name)
            if pair in self._compared_components:
                return
            self._compared_components.add(pair)
            location = f"components.schemas.{expected_name}"
            # Nullability belongs to the referencing site, not the component itself.
            if expected_schema["nullable"] != actual_schema["nullable"]:
                self._add(
                    Severity.ERROR,
                    f"{location} nullable",
                    f"expected {expected_schema['nullable']}, found {actual_schema['nullable']}",
                )

        for key in _ANNOTATION_KEYWORDS:
            if key == "title":
                continue
            if expected_schema.get(key) != actual_schema.get(key):
                self._add(
                    Severity.INFO,
                    f"{location} {key}",
                    f"expected {expected_schema.get(key)!r}, found {actual_schema.get(key)!r}",
                )

        alternate_types = self._compare_types(location, expected_schema, actual_schema)

        for key in _VALIDATION_KEYWORDS:
            expected_value = expected_schema.get(key)
            actual_value = actual_schema.get(key)
            if isinstance(expected_value, dict) and isinstance(actual_value, dict):
                # additionalProperties can itself be a schema.
                self._compare_schema(f"{location} {key}", expected_value, actual_value)
                continue
            if key == "enum":
                matches = _as_set(expected_value) == _as_set(actual_value)
            else:
                matches = expected_value == actual_value
            if matches:
                continue
            if expected_value is None:
                # The implementation is stricter or more explicit than the specification.
                severity = Severity.WARN
            elif alternate_types and key in ("format", "pattern"):
                # The pattern and format belong to the alternate (string) form of the value.
                severity = Severity.INFO
            else:
                severity = Severity.ERROR
            self._add(
                severity,
                f"{location} {key}",
                f"expected {expected_value!r}, found {actual_value!r}",
            )

        expected_required = set(expected_schema.get("required", []))
        actual_required = set(actual_schema.get("required", []))
        if missing_required := sorted(expected_required - actual_required):
            self._add(
                Severity.ERROR,
                f"{location} required",
                f"not required by the implementation: {missing_required}",
            )
        if extra_required := sorted(actual_required - expected_required):
            self._add(
                Severity.WARN,
                f"{location} required",
                f"not required by the specification: {extra_required}",
            )

        self._compare_properties(location, expected_schema, actual_schema)

        if "items" in expected_schema or "items" in actual_schema:
            if "items" not in actual_schema:
                self._add(Severity.ERROR, f"{location} items", "schema is not implemented")
            elif "items" not in expected_schema:
                self._add(Severity.ERROR, f"{location} items", "schema is not in the specification")
            else:
                self._compare_schema(
                    f"{location} items", expected_schema["items"], actual_schema["items"]
                )

        for key in _COMPOSITION_KEYWORDS:
            self._compare_composition(location, key, expected_schema, actual_schema)

    def _compare_types(
        self, location: str, expected: dict[str, Any], actual: dict[str, Any]
    ) -> bool:
        """Reports type differences; returns True when only alternate types differ."""
        expected_types = expected["types"]
        actual_types = actual["types"]
        if expected_types == actual_types:
            return False
        # A schema that only adds or drops alternate types (e.g. [integer, string] vs
        # integer) still shares its base type.
        if (
            expected_types
            and actual_types
            and (expected_types <= actual_types or actual_types <= expected_types)
        ):
            self._add(
                Severity.INFO,
                f"{location} type",
                f"alternate types differ: expected {sorted(expected_types)}, "
                f"found {sorted(actual_types)}",
            )
            return True
        self._add(
            Severity.ERROR,
            f"{location} type",
            f"expected {sorted(expected_types)}, found {sorted(actual_types)}",
        )
        return False

    def _compare_properties(
        self, location: str, expected: dict[str, Any], actual: dict[str, Any]
    ) -> None:
        expected_properties = expected.get("properties", {})
        actual_properties = actual.get("properties", {})
        for name in sorted(expected_properties.keys() - actual_properties.keys()):
            self._add(Severity.ERROR, f"{location}.{name}", "property is not implemented")
        for name in sorted(actual_properties.keys() - expected_properties.keys()):
            self._add(Severity.WARN, f"{location}.{name}", "property is not in the specification")
        for name in sorted(expected_properties.keys() & actual_properties.keys()):
            self._compare_schema(
                f"{location}.{name}", expected_properties[name], actual_properties[name]
            )

    def _compare_composition(
        self, location: str, key: str, expected: dict[str, Any], actual: dict[str, Any]
    ) -> None:
        expected_branches = expected.get(key)
        actual_branches = actual.get(key)
        if expected_branches is None and actual_branches is None:
            return
        if (
            expected_branches is None
            or actual_branches is None
            or len(expected_branches) != len(actual_branches)
        ):
            self._add(
                Severity.ERROR,
                f"{location} {key}",
                f"expected {expected_branches!r}, found {actual_branches!r}",
            )
            return
        for index, (expected_branch, actual_branch) in enumerate(
            zip(expected_branches, actual_branches, strict=True)
        ):
            self._compare_schema(f"{location} {key}[{index}]", expected_branch, actual_branch)

    def _compare_unreferenced_components(self) -> None:
        expected_schemas = self._expected.get("components", {}).get("schemas", {})
        actual_schemas = self._actual.get("components", {}).get("schemas", {})
        paired_expected = {expected for expected, _ in self._compared_components}
        paired_actual = {actual for _, actual in self._compared_components}
        for name in sorted(expected_schemas.keys() - paired_expected):
            location = f"components.schemas.{name}"
            if name in actual_schemas:
                self._compare_schema(
                    location,
                    {"$ref": f"#/components/schemas/{name}"},
                    {"$ref": f"#/components/schemas/{name}"},
                )
                paired_actual.add(name)
            else:
                self._add(Severity.ERROR, location, "schema is not implemented")
        for name in sorted(actual_schemas.keys() - paired_actual):
            self._add(
                Severity.WARN, f"components.schemas.{name}", "schema is not in the specification"
            )


def _operations(document: dict[str, Any]) -> dict[tuple[str, str], dict[str, Any]]:
    return {
        (path, method): operation
        for path, operations in document.get("paths", {}).items()
        for method, operation in operations.items()
        if method in HTTP_METHODS
    }


def _operation_location(key: tuple[str, str]) -> str:
    path, method = key
    return f"{method.upper()} {path}"


def _normalize_security(security: list[dict[str, list[str]]]) -> list[dict[str, list[str]]]:
    return sorted(
        (
            {name: sorted(scopes) for name, scopes in requirement.items()}
            for requirement in security
        ),
        key=repr,
    )


def _resolve(document: dict[str, Any], node: Any) -> Any:
    seen = set()
    while isinstance(node, dict) and "$ref" in node:
        reference = node["$ref"]
        if reference in seen:
            raise ValueError(f"Circular reference: {reference}")
        seen.add(reference)
        target: Any = document
        for part in reference.removeprefix("#/").split("/"):
            target = target[part.replace("~1", "/").replace("~0", "~")]
        # OpenAPI 3.1 allows siblings next to $ref; they override the target.
        siblings = {key: value for key, value in node.items() if key != "$ref"}
        node = {**target, **siblings} if siblings else target
    return node


def _component_name(schema: Any) -> str | None:
    if isinstance(schema, dict):
        reference = schema.get("$ref", "")
        if reference.startswith("#/components/schemas/"):
            return reference.removeprefix("#/components/schemas/")
    return None


def _normalize(document: dict[str, Any], schema: Any) -> dict[str, Any]:
    """Resolves a schema and expresses its type and nullability uniformly.

    OpenAPI 3.1 can declare nullability as ``type: [string, "null"]``, as a
    ``oneOf``/``anyOf`` with a ``{type: "null"}`` branch, or (3.0) as ``nullable``.
    The result carries ``types`` (non-null type names) and ``nullable`` instead.
    """
    resolved = dict(_resolve(document, schema) or {})
    declared_type = resolved.pop("type", None)
    if isinstance(declared_type, list):
        types = set(declared_type)
    elif declared_type is None:
        types = set()
    else:
        types = {declared_type}
    nullable = bool(resolved.pop("nullable", False)) or "null" in types
    types.discard("null")

    for key in ("oneOf", "anyOf"):
        branches = resolved.get(key)
        if not branches:
            continue
        non_null = [branch for branch in branches if not _is_null_schema(document, branch)]
        if len(non_null) == len(branches):
            continue
        nullable = True
        if len(non_null) == 1 and not types:
            # The wrapper only adds nullability; fold the remaining branch into the schema.
            del resolved[key]
            inner = _normalize(document, non_null[0])
            nullable = nullable or inner.pop("nullable")
            types = inner.pop("types")
            resolved = {**inner, **resolved}
        else:
            resolved[key] = non_null

    resolved["types"] = types
    resolved["nullable"] = nullable
    return resolved


def _unwrap_nullable_reference(document: dict[str, Any], schema: Any) -> tuple[Any, bool]:
    """Turns ``oneOf``/``anyOf: [{$ref}, {type: "null"}]`` into the ``$ref`` plus a flag."""
    if not isinstance(schema, dict) or "type" in schema:
        return schema, False
    for key in ("oneOf", "anyOf"):
        branches = schema.get(key) or []
        non_null = [branch for branch in branches if not _is_null_schema(document, branch)]
        if len(branches) == 2 and len(non_null) == 1 and _component_name(non_null[0]):
            reference = non_null[0]
            # Annotations on the wrapper (e.g. a description) still apply to the property.
            annotations = {k: schema[k] for k in _ANNOTATION_KEYWORDS if k in schema}
            return ({**annotations, **reference} if annotations else reference), True
    return schema, False


def _is_null_schema(document: dict[str, Any], schema: Any) -> bool:
    resolved = _resolve(document, schema)
    return isinstance(resolved, dict) and resolved.get("type") == "null"


def _as_set(values: Any) -> frozenset | None:
    if values is None:
        return None
    return frozenset(repr(value) for value in values)
