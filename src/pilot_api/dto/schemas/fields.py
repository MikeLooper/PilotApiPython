from dataclasses import dataclass
from datetime import datetime
from typing import Annotated

from annotated_types import Ge, Le, Len
from pydantic import AfterValidator, GetJsonSchemaHandler, Strict
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import CoreSchema

# Bounds of the Northwind column types, as declared by the shared definition.
INT16_MAX = 32767
INT32_MAX = 2147483647
MONEY_MIN = -922337203685477.5
MONEY_MAX = 922337203685477.5
SQL_DATETIME_MIN = datetime(1753, 1, 1)


@dataclass(frozen=True)
class SchemaFormat:
    # The definition's format keyword for a numeric value. Only documented: the numeric
    # bounds already enforce it. Not a Field(json_schema_extra=...) because FastAPI drops
    # that from nested parameter types.
    format: str

    def __get_pydantic_json_schema__(
        self, schema: CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        json_schema = handler(schema)
        json_schema["format"] = self.format
        return json_schema


def _within_sql_datetime_range(value: datetime) -> datetime:
    # datetime cannot pass the 9999-12-31 upper bound, so only the lower one needs a check.
    if value.replace(tzinfo=None) < SQL_DATETIME_MIN:
        raise ValueError("Input should be on or after 1753-01-01")
    return value


def _before_now(value: datetime) -> datetime:
    if value >= datetime.now(value.tzinfo):
        raise ValueError("Input should be earlier than the current date")
    return value


# Path and query values arrive as text, so these *Param types must convert them. Everything
# else is Strict: the definition types JSON numbers as numbers only, so "1" is not a valid 1.
Int32Param = Annotated[int, SchemaFormat("int32")]
Int32KeyParam = Annotated[Int32Param, Ge(1), Le(INT32_MAX)]
Int32 = Annotated[Int32Param, Strict()]
Int32Key = Annotated[Int32KeyParam, Strict()]
# Every string key in the definition has the shape of Northwind's nchar(5) customer ID.
StringKey = Annotated[str, Len(5, 5)]
PositiveInt16 = Annotated[int, Strict(), Ge(1), Le(INT16_MAX), SchemaFormat("int16")]
NonNegativeInt16 = Annotated[int, Strict(), Ge(0), Le(INT16_MAX), SchemaFormat("int16")]
Fraction = Annotated[float, Strict(), Ge(0), Le(1), SchemaFormat("float")]
Money = Annotated[float, Strict(), Ge(0), Le(MONEY_MAX), SchemaFormat("double")]
SignedMoney = Annotated[float, Strict(), Ge(MONEY_MIN), Le(MONEY_MAX), SchemaFormat("double")]
SqlDateTime = Annotated[datetime, AfterValidator(_within_sql_datetime_range)]
PastSqlDateTime = Annotated[SqlDateTime, AfterValidator(_before_now)]
