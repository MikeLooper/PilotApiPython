import uuid

import pytest
from starlette.requests import Request
from starlette.responses import Response

from pilot_api.config.request_settings import (
    RequestSettings,
    get_current_request_settings,
    request_settings_var,
)


def _request(headers: dict[str, str]) -> Request:
    raw_headers = [(name.lower().encode(), value.encode()) for name, value in headers.items()]
    return Request({"type": "http", "headers": raw_headers})


def test_from_request_uses_correlation_id_header_when_provided() -> None:
    request = _request({"X-Correlation-Id": "corr-1"})

    request_settings = RequestSettings.from_request(request)

    assert request_settings.correlation_id == "corr-1"


def test_from_request_reads_correlation_id_header_case_insensitively() -> None:
    request = _request({"x-correlation-id": "corr-1"})

    request_settings = RequestSettings.from_request(request)

    assert request_settings.correlation_id == "corr-1"


def test_from_request_generates_guid_correlation_id_when_header_missing() -> None:
    request_settings = RequestSettings.from_request(_request({}))

    assert uuid.UUID(request_settings.correlation_id)
    assert request_settings.correlation_id != request_settings.request_id


def test_from_request_generates_guid_correlation_id_when_header_blank() -> None:
    request_settings = RequestSettings.from_request(_request({"X-Correlation-Id": ""}))

    assert uuid.UUID(request_settings.correlation_id)


def test_from_request_assigns_unique_request_id_per_request() -> None:
    first = RequestSettings.from_request(_request({}))
    second = RequestSettings.from_request(_request({}))

    assert uuid.UUID(first.request_id)
    assert first.request_id != second.request_id


def test_from_request_ignores_inbound_request_id_header() -> None:
    request_settings = RequestSettings.from_request(_request({"X-Request-Id": "client-req"}))

    assert request_settings.request_id != "client-req"


def test_from_request_uses_caller_name_header_when_provided() -> None:
    request_settings = RequestSettings.from_request(_request({"X-Caller-Name": "PilotAngularUi"}))

    assert request_settings.caller_name == "PilotAngularUi"


def test_from_request_reads_caller_name_header_case_insensitively() -> None:
    request_settings = RequestSettings.from_request(_request({"x-caller-name": "PilotAngularUi"}))

    assert request_settings.caller_name == "PilotAngularUi"


@pytest.mark.parametrize("headers", [{}, {"X-Caller-Name": ""}])
def test_from_request_leaves_caller_name_none_when_header_missing_or_blank(
    headers: dict[str, str],
) -> None:
    request_settings = RequestSettings.from_request(_request(headers))

    assert request_settings.caller_name is None


def test_apply_to_does_not_echo_caller_name() -> None:
    request_settings = RequestSettings(
        request_id="req-1", correlation_id="corr-1", caller_name="PilotAngularUi"
    )
    response = Response()

    request_settings.apply_to(response)

    assert "X-Caller-Name" not in response.headers


def test_apply_to_sets_correlation_and_request_id_response_headers() -> None:
    request_settings = RequestSettings(request_id="req-1", correlation_id="corr-1")
    response = Response()

    request_settings.apply_to(response)

    assert response.headers["X-Correlation-Id"] == "corr-1"
    assert response.headers["X-Request-Id"] == "req-1"


def test_get_current_request_settings_returns_none_outside_a_request() -> None:
    assert get_current_request_settings() is None


def test_get_current_request_settings_returns_value_set_for_request() -> None:
    request_settings = RequestSettings(request_id="req-1", correlation_id="corr-1")
    token = request_settings_var.set(request_settings)
    try:
        current = get_current_request_settings()
    finally:
        request_settings_var.reset(token)

    assert current is request_settings
