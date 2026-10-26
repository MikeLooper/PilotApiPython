from pydantic import Field

from pilot_api.dto.schemas.base import DtoBase
from pilot_api.dto.schemas.fields import Int32Key, SignedMoney, SqlDateTime, StringKey


class OrdersDto(DtoBase):
    customerId: StringKey | None = None
    employeeId: Int32Key | None = None
    freight: SignedMoney | None = None
    orderDate: SqlDateTime | None = None
    orderId: Int32Key | None = None
    requiredDate: SqlDateTime | None = None
    shipAddress: str | None = Field(default=None, max_length=60)
    shipCity: str | None = Field(default=None, max_length=15)
    shipCountry: str | None = Field(default=None, max_length=15)
    shipName: str | None = Field(default=None, max_length=40)
    shippedDate: SqlDateTime | None = None
    shipPostalCode: str | None = Field(default=None, max_length=10)
    shipRegion: str | None = Field(default=None, max_length=15)
    shipVia: Int32Key | None = None
