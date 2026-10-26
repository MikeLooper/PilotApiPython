"""Validates the application's OpenAPI document against the shared specification.

- ERROR findings fail test_openapi_compliance_errors_none_found.
- WARN findings are emitted as OpenApiComplianceWarning (see the pytest warnings summary).
- INFO findings are logged by test_openapi_compliance_information_logged
  (run with ``-o log_cli=true --log-cli-level=INFO`` to see them).
"""

import logging
import warnings
from pathlib import Path
from typing import Any

import pytest
import yaml
from fastapi.testclient import TestClient
from openapi_comparator import Finding, OpenApiComparator, Severity

from pilot_api.main import app

pytestmark = pytest.mark.integration

SPECIFICATION_PATH = (
    Path(__file__).resolve().parents[2]
    / "shared"
    / "PilotSharedSource"
    / "OpenAPI"
    / "PilotApi_v1.yaml"
)

logger = logging.getLogger(__name__)

# The implementation bounds SQL money columns at +/-922337203685477.5, whereas the
# specification declares 922337203685477.5807 / -922337203685477.5808. These known
# deviations are accepted and are not reported as compliance errors.
ACCEPTED_DEVIATIONS = frozenset(
    {
        "components.schemas.OrderDetailsDto.unitPrice maximum",
        "components.schemas.OrdersDto.freight minimum",
        "components.schemas.OrdersDto.freight maximum",
        "components.schemas.ProductsDto.unitPrice maximum",
    }
)


class OpenApiComplianceWarning(UserWarning):
    pass


@pytest.fixture(scope="module")
def specification() -> dict[str, Any]:
    if not SPECIFICATION_PATH.is_file():
        pytest.skip(
            f"{SPECIFICATION_PATH} not found; run 'git submodule update --init' to fetch it."
        )
    with SPECIFICATION_PATH.open(encoding="utf-8") as specification_file:
        return yaml.safe_load(specification_file)


@pytest.fixture(scope="module")
def implementation() -> dict[str, Any]:
    response = TestClient(app).get("/openapi.json")
    assert response.status_code == 200
    return response.json()


@pytest.fixture(scope="module")
def findings(specification: dict[str, Any], implementation: dict[str, Any]) -> list[Finding]:
    return OpenApiComparator(specification, implementation).compare()


def _with_severity(findings: list[Finding], severity: Severity) -> list[Finding]:
    return [finding for finding in findings if finding.severity == severity]


def test_openapi_compliance_errors_none_found(findings: list[Finding]) -> None:
    errors = [
        error
        for error in _with_severity(findings, Severity.ERROR)
        if error.location not in ACCEPTED_DEVIATIONS
    ]

    assert not errors, (
        f"{len(errors)} OpenAPI compliance error(s) against {SPECIFICATION_PATH.name}:\n"
        + "\n".join(str(error) for error in errors)
    )


def test_openapi_compliance_warnings_reported(findings: list[Finding]) -> None:
    for finding in _with_severity(findings, Severity.WARN):
        warnings.warn(str(finding), OpenApiComplianceWarning, stacklevel=1)


def test_openapi_compliance_information_logged(findings: list[Finding]) -> None:
    for finding in _with_severity(findings, Severity.INFO):
        logger.info("%s", finding)
