import asyncio

from pilot_api.validation.rules import get_api_version


def test_get_api_version_returns_header_value_when_provided() -> None:
    result = asyncio.run(get_api_version("1"))
    assert result == "1"


def test_get_api_version_returns_none_when_missing() -> None:
    result = asyncio.run(get_api_version(None))
    assert result is None
