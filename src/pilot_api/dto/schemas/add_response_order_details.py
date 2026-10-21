from pydantic import field_validator

from pilot_api.dto.schemas.base import DtoBase, coerce_number


class AddResponseOrderDetailsDto(DtoBase):
    orderID: int
    productID: int

    @field_validator("orderID", "productID", mode="before")
    @classmethod
    def validate_add_response_order_details_numbers(cls, value: object) -> object:
        return coerce_number(value)
