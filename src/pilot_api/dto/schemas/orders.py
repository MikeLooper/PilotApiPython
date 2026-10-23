from datetime import datetime

from pilot_api.dto.schemas.base import DtoBase


class OrdersDto(DtoBase):
    customerId: str | None = None
    employeeId: int | None = None
    freight: float | None = None
    orderDate: datetime | None = None
    orderId: int | None = None
    requiredDate: datetime | None = None
    shipAddress: str | None = None
    shipCity: str | None = None
    shipCountry: str | None = None
    shipName: str | None = None
    shippedDate: datetime | None = None
    shipPostalCode: str | None = None
    shipRegion: str | None = None
    shipVia: int | None = None
