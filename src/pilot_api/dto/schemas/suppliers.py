from pydantic import field_validator

from pilot_api.dto.schemas.base import DtoBase, coerce_number


class SuppliersDto(DtoBase):
    address: str | None = None
    city: str | None = None
    companyName: str | None
    contactName: str | None = None
    contactTitle: str | None = None
    country: str | None = None
    fax: str | None = None
    homePage: str | None = None
    phone: str | None = None
    postalCode: str | None = None
    region: str | None = None
    supplierID: int

    @field_validator("supplierID", mode="before")
    @classmethod
    def validate_supplier_id(cls, value: object) -> object:
        return coerce_number(value)
