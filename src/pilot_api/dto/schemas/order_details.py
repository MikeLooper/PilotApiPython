from pydantic import Field

from pilot_api.dto.schemas.base import DtoBase
from pilot_api.dto.schemas.fields import Int32Key, Money, PositiveInt16


class OrderDetailsDto(DtoBase):
    discount: float = Field(ge=0, le=1)
    orderId: Int32Key
    productId: Int32Key
    quantity: PositiveInt16
    unitPrice: Money
