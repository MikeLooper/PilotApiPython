from pydantic import field_validator

from pilot_api.dto.schemas.base import DtoBase, coerce_number


class ShippersDto(DtoBase):
    companyName: str | None
    phone: str | None = None
    shipperID: int | None = None

    @field_validator("shipperID", mode="before")
    @classmethod
    def validate_shipper_id(cls, value: object) -> object:
        return coerce_number(value)
