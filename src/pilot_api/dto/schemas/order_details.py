from pydantic import field_validator

from pilot_api.dto.schemas.base import DtoBase, coerce_number


class OrderDetailsDto(DtoBase):
    discount: float
    orderID: int
    productID: int
    quantity: int
    unitPrice: float

    @field_validator("orderID", "productID", "quantity", "unitPrice", "discount", mode="before")
    @classmethod
    def validate_order_detail_numbers(cls, value: object) -> object:
        return coerce_number(value)
