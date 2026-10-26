from pydantic import ConfigDict, Field

from pilot_api.dto.schemas.base import DtoBase, omit_required
from pilot_api.dto.schemas.fields import INT32_MAX


class AddResponseIntDto(DtoBase):
    # Always returned, but the shared definition does not list id as required.
    model_config = ConfigDict(json_schema_extra=omit_required)

    # Not Int32Key: the definition types this as int64 and gives no string-form length.
    id: int = Field(
        ge=1,
        le=INT32_MAX,
        json_schema_extra={"format": "int64", "pattern": r"^-?(?:0|[1-9]\d*)$"},
    )
