from datetime import UTC, datetime

import pytest
from pydantic import TypeAdapter, ValidationError

from pilot_api.dto.schemas.fields import (
    INT16_MAX,
    INT32_MAX,
    MONEY_MAX,
    MONEY_MIN,
    Fraction,
    Int32,
    Int32Key,
    Int32KeyParam,
    Int32Param,
    Money,
    NonNegativeInt16,
    PastSqlDateTime,
    PositiveInt16,
    SignedMoney,
    SqlDateTime,
    StringKey,
)


@pytest.mark.parametrize("value", [1, INT32_MAX])
def test_int32_key_within_range_is_accepted(value: int) -> None:
    assert TypeAdapter(Int32Key).validate_python(value) == value


@pytest.mark.parametrize(
    "annotation",
    [Int32, Int32Key, PositiveInt16, NonNegativeInt16, Fraction, Money, SignedMoney],
)
@pytest.mark.parametrize("value", ["1", True])
def test_body_number_rejects_other_json_types(annotation: object, value: object) -> None:
    with pytest.raises(ValidationError):
        TypeAdapter(annotation).validate_python(value)


@pytest.mark.parametrize("annotation", [Fraction, Money, SignedMoney])
def test_body_float_accepts_json_integer(annotation: object) -> None:
    assert TypeAdapter(annotation).validate_python(1) == 1


@pytest.mark.parametrize("annotation", [Int32Param, Int32KeyParam])
def test_parameter_int_converts_url_text(annotation: object) -> None:
    assert TypeAdapter(annotation).validate_python("42") == 42


@pytest.mark.parametrize("value", ["0", "2147483648", "abc"])
def test_int32_key_param_rejects_invalid_url_text(value: str) -> None:
    with pytest.raises(ValidationError):
        TypeAdapter(Int32KeyParam).validate_python(value)


@pytest.mark.parametrize("value", [0, -1, INT32_MAX + 1])
def test_int32_key_outside_range_is_rejected(value: int) -> None:
    with pytest.raises(ValidationError):
        TypeAdapter(Int32Key).validate_python(value)


@pytest.mark.parametrize("annotation", [Int32Key, Int32KeyParam])
def test_int32_key_json_schema_documents_format_and_bounds(annotation: object) -> None:
    schema = TypeAdapter(annotation).json_schema()

    assert schema == {
        "type": "integer",
        "format": "int32",
        "minimum": 1,
        "maximum": INT32_MAX,
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


@pytest.mark.parametrize(
    ("annotation", "schema_format"),
    [
        (PositiveInt16, "int16"),
        (NonNegativeInt16, "int16"),
        (Fraction, "float"),
        (Money, "double"),
        (SignedMoney, "double"),
    ],
)
def test_number_json_schema_documents_format(annotation: object, schema_format: str) -> None:
    assert TypeAdapter(annotation).json_schema()["format"] == schema_format


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
