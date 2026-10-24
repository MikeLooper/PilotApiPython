from pilot_api.dto.schemas.base import DtoBase


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
    supplierId: int | None = None
