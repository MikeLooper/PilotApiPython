from typing import Any

from pydantic import BaseModel, ConfigDict


class DtoBase(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="forbid")


def coerce_number(value: Any) -> Any:
    if isinstance(value, str) and value.strip() != "":
        if "." in value:
            return float(value)
        return int(value)
    return value
