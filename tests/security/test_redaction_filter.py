import logging

from pilot_api.config.logging_config import SensitiveDataFilter


def _filtered_record(msg: str, args: tuple = ()) -> logging.LogRecord:
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg=msg,
        args=args,
        exc_info=None,
    )
    SensitiveDataFilter().filter(record)
    return record


def test_redacts_password_in_message() -> None:
    record = _filtered_record("Connection failed password=SuperSecret123")

    assert "SuperSecret123" not in record.getMessage()
    assert "[REDACTED]" in record.getMessage()


def test_redacts_pwd_in_message_case_insensitively() -> None:
    record = _filtered_record("db PWD: TopSecret!")

    assert "TopSecret!" not in record.getMessage()


def test_redacts_password_in_args() -> None:
    record = _filtered_record("Connection string: %s", args=("password=SuperSecret123",))

    assert "SuperSecret123" not in record.getMessage()


def test_redacts_basic_auth_header() -> None:
    record = _filtered_record("Header dump Authorization: Basic dXNlcjpwYXNz")

    assert "dXNlcjpwYXNz" not in record.getMessage()


def test_leaves_unrelated_text_untouched() -> None:
    record = _filtered_record("Authentication succeeded user_id=working_admin_user")

    assert record.getMessage() == "Authentication succeeded user_id=working_admin_user"
