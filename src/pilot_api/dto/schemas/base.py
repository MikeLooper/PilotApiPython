from typing import Any

from pydantic import BaseModel, ConfigDict


def _omit_defaults(schema: dict[str, Any]) -> None:
    # Defaults fill in omitted fields at runtime; the shared definition does not declare them.
    for property_schema in schema.get("properties", {}).values():
        property_schema.pop("default", None)


def omit_required(schema: dict[str, Any]) -> None:
    schema.pop("required", None)


class DtoBase(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True, extra="forbid", json_schema_extra=_omit_defaults
    )
