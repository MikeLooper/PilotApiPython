from pilot_api.dto.schemas.base import DtoBase


class CustomersDto(DtoBase):
    address: str | None = None
    city: str | None = None
    companyName: str | None
    contactName: str | None = None
    contactTitle: str | None = None
    country: str | None = None
    customerID: str | None
    fax: str | None = None
    phone: str | None = None
    postalCode: str | None = None
    region: str | None = None
