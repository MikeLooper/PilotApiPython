from pydantic import field_validator

from pilot_api.dto.schemas.base import DtoBase, coerce_number


class TerritoriesDto(DtoBase):
    territoryID: str
    territoryDescription: str
    regionID: int

    @field_validator("regionID", mode="before")
    @classmethod
    def validate_region_id(cls, value: object) -> object:
        return coerce_number(value)
