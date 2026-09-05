import pytest

from pilot_api.security.security_helper import is_authorized

READ_METHODS = ["GET", "HEAD", "OPTIONS", "QUERY", "TRACE"]
WRITE_METHODS = ["PATCH", "POST", "PUT"]
ADMIN_METHODS = ["DELETE"]


@pytest.mark.parametrize("method", READ_METHODS)
def test_read_only_role_can_read(method: str) -> None:
    assert is_authorized("read_only_role", method) is True


@pytest.mark.parametrize("method", WRITE_METHODS + ADMIN_METHODS)
def test_read_only_role_cannot_write_or_delete(method: str) -> None:
    assert is_authorized("read_only_role", method) is False


@pytest.mark.parametrize("method", READ_METHODS + WRITE_METHODS)
def test_read_write_role_can_read_and_write(method: str) -> None:
    assert is_authorized("read_write_role", method) is True


@pytest.mark.parametrize("method", ADMIN_METHODS)
def test_read_write_role_cannot_delete(method: str) -> None:
    assert is_authorized("read_write_role", method) is False


@pytest.mark.parametrize("method", READ_METHODS + WRITE_METHODS + ADMIN_METHODS)
def test_admin_role_can_do_everything(method: str) -> None:
    assert is_authorized("admin_role", method) is True


@pytest.mark.parametrize("method", READ_METHODS + WRITE_METHODS + ADMIN_METHODS)
def test_unknown_or_missing_role_is_denied_everywhere(method: str) -> None:
    assert is_authorized(None, method) is False
    assert is_authorized("made_up_role", method) is False
