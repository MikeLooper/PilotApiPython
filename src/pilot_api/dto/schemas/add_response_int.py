from pydantic import ConfigDict, Field

from pilot_api.dto.schemas.base import DtoBase, omit_required


class AddResponseIntDto(DtoBase):
    # Always returned, but the shared definition does not list id as required.
    model_config = ConfigDict(json_schema_extra=omit_required)

    id: int = Field(json_schema_extra={"format": "int64", "pattern": r"^-?(?:0|[1-9]\d*)$"})
