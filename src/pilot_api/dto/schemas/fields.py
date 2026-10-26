from dataclasses import dataclass
from datetime import datetime
from typing import Annotated

from annotated_types import Ge, Le, Len
from pydantic import AfterValidator, GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import CoreSchema

# Bounds of the Northwind column types, as declared by the shared definition.
INT16_MAX = 32767
INT32_MAX = 2147483647
MONEY_MIN = -922337203685477.5
MONEY_MAX = 922337203685477.5
SQL_DATETIME_MIN = datetime(1753, 1, 1)


@dataclass(frozen=True)
class StringFormLength:
    # The definition types numeric values as [integer, string] and bounds the length of
    # the string form. Only documented: the numeric bounds already enforce it. Not a
    # Field(json_schema_extra=...) because FastAPI drops that from nested parameter types.
    min_length: int
    max_length: int

    def __get_pydantic_json_schema__(
        self, schema: CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        json_schema = handler(schema)
        json_schema.update(minLength=self.min_length, maxLength=self.max_length)
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


Int32Key = Annotated[int, Ge(1), Le(INT32_MAX), StringFormLength(1, 10)]
# Every string key in the definition has the shape of Northwind's nchar(5) customer ID.
StringKey = Annotated[str, Len(5, 5)]
PositiveInt16 = Annotated[int, Ge(1), Le(INT16_MAX), StringFormLength(1, 5)]
NonNegativeInt16 = Annotated[int, Ge(0), Le(INT16_MAX), StringFormLength(1, 5)]
Money = Annotated[float, Ge(0), Le(MONEY_MAX)]
SignedMoney = Annotated[float, Ge(MONEY_MIN), Le(MONEY_MAX)]
SqlDateTime = Annotated[datetime, AfterValidator(_within_sql_datetime_range)]
PastSqlDateTime = Annotated[SqlDateTime, AfterValidator(_before_now)]
