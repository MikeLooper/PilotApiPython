from datetime import UTC, datetime

import pytest
from pydantic import TypeAdapter, ValidationError

from pilot_api.dto.schemas.fields import (
    INT16_MAX,
    INT32_MAX,
    MONEY_MAX,
    MONEY_MIN,
    Int32Key,
    Money,
    NonNegativeInt16,
    PastSqlDateTime,
    PositiveInt16,
    SignedMoney,
    SqlDateTime,
    StringKey,
)


@pytest.mark.parametrize("value", [1, INT32_MAX, "42"])
def test_int32_key_within_range_is_accepted(value: int | str) -> None:
    assert TypeAdapter(Int32Key).validate_python(value) == int(value)


@pytest.mark.parametrize("value", [0, -1, INT32_MAX + 1])
def test_int32_key_outside_range_is_rejected(value: int) -> None:
    with pytest.raises(ValidationError):
        TypeAdapter(Int32Key).validate_python(value)


def test_int32_key_json_schema_documents_numeric_and_string_bounds() -> None:
    schema = TypeAdapter(Int32Key).json_schema()

    assert schema == {
        "type": "integer",
        "minimum": 1,
        "maximum": INT32_MAX,
        "minLength": 1,
        "maxLength": 10,
    }


def test_string_key_with_five_characters_is_accepted() -> None:
    assert TypeAdapter(StringKey).validate_python("ALFKI") == "ALFKI"


@pytest.mark.parametrize("value", ["ALFK", "ALFKIX", ""])
def test_string_key_with_other_length_is_rejected(value: str) -> None:
    with pytest.raises(ValidationError):
        TypeAdapter(StringKey).validate_python(value)


@pytest.mark.parametrize(("annotation", "minimum"), [(PositiveInt16, 1), (NonNegativeInt16, 0)])
def test_int16_bounds_are_enforced(annotation: object, minimum: int) -> None:
    adapter = TypeAdapter(annotation)

    assert adapter.validate_python(minimum) == minimum
    assert adapter.validate_python(INT16_MAX) == INT16_MAX
    with pytest.raises(ValidationError):
        adapter.validate_python(minimum - 1)
    with pytest.raises(ValidationError):
        adapter.validate_python(INT16_MAX + 1)


def test_int16_json_schema_documents_string_form_length() -> None:
    schema = TypeAdapter(PositiveInt16).json_schema()

    assert (schema["minLength"], schema["maxLength"]) == (1, 5)


def test_money_rejects_negative_value() -> None:
    adapter = TypeAdapter(Money)

    assert adapter.validate_python(0) == 0
    assert adapter.validate_python(MONEY_MAX) == MONEY_MAX
    with pytest.raises(ValidationError):
        adapter.validate_python(-0.01)


def test_signed_money_accepts_negative_value_down_to_minimum() -> None:
    adapter = TypeAdapter(SignedMoney)

    assert adapter.validate_python(-12.5) == -12.5
    assert adapter.validate_python(MONEY_MIN) == MONEY_MIN
    with pytest.raises(ValidationError):
        adapter.validate_python(MONEY_MIN * 2)


@pytest.mark.parametrize(
    "value", [datetime(1753, 1, 1), datetime(1753, 1, 1, tzinfo=UTC), datetime(9999, 12, 31)]
)
def test_sql_datetime_within_range_is_accepted(value: datetime) -> None:
    assert TypeAdapter(SqlDateTime).validate_python(value) == value


def test_sql_datetime_before_1753_is_rejected() -> None:
    with pytest.raises(ValidationError, match="on or after 1753-01-01"):
        TypeAdapter(SqlDateTime).validate_python(datetime(1752, 12, 31, 23, 59, 59))


def test_past_sql_datetime_accepts_past_date() -> None:
    value = datetime(1968, 12, 8, tzinfo=UTC)

    assert TypeAdapter(PastSqlDateTime).validate_python(value) == value


@pytest.mark.parametrize("value", [datetime(9999, 1, 1), datetime(9999, 1, 1, tzinfo=UTC)])
def test_past_sql_datetime_rejects_future_date(value: datetime) -> None:
    with pytest.raises(ValidationError, match="earlier than the current date"):
        TypeAdapter(PastSqlDateTime).validate_python(value)


def test_past_sql_datetime_still_enforces_sql_range() -> None:
    with pytest.raises(ValidationError, match="on or after 1753-01-01"):
        TypeAdapter(PastSqlDateTime).validate_python(datetime(1700, 1, 1))
