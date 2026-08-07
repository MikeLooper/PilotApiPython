from datetime import datetime

from pydantic import field_validator

from pilot_api.dto.schemas.base import DtoBase, coerce_number


class OrdersDto(DtoBase):
    customerID: str | None = None
    employeeID: int | None = None
    freight: float | None = None
    orderDate: datetime | None = None
    orderID: int
    requiredDate: datetime | None = None
    shipAddress: str | None = None
    shipCity: str | None = None
    shipCountry: str | None = None
    shipName: str | None = None
    shippedDate: datetime | None = None
    shipPostalCode: str | None = None
    shipRegion: str | None = None
    shipVia: int | None = None

    @field_validator("orderID", "employeeID", "shipVia", "freight", mode="before")
    @classmethod
    def validate_order_numbers(cls, value: object) -> object:
        return coerce_number(value)
