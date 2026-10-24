from enum import IntEnum
from typing import Any

from pydantic import GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import CoreSchema


class DataSourceTypes(IntEnum):
    """Enums for the available data sources."""

    UNRECOGNIZED = 0
    POSTGRESQL = 1
    SQLSERVER = 2

    @classmethod
    def __get_pydantic_json_schema__(
        cls, core_schema: CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        json_schema = handler(core_schema)
        # The shared definition types this as a plain integer without listing its values.
        definition: dict[str, Any] = handler.resolve_ref_schema(json_schema)
        definition.pop("enum", None)
        return json_schema
