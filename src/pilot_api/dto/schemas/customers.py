from pydantic import Field

from pilot_api.dto.schemas.base import DtoBase
from pilot_api.dto.schemas.fields import StringKey


class CustomersDto(DtoBase):
    address: str | None = Field(default=None, max_length=60)
    city: str | None = Field(default=None, max_length=15)
    companyName: str = Field(min_length=1, max_length=40)
    contactName: str | None = Field(default=None, max_length=30)
    contactTitle: str | None = Field(default=None, max_length=30)
    country: str | None = Field(default=None, max_length=15)
    customerId: StringKey
    fax: str | None = Field(default=None, max_length=24)
    phone: str | None = Field(default=None, max_length=24)
    postalCode: str | None = Field(default=None, max_length=10)
    region: str | None = Field(default=None, max_length=15)
