from pilot_api.dto.schemas.base import DtoBase
from pilot_api.dto.schemas.fields import Fraction, Int32Key, Money, PositiveInt16


class OrderDetailsDto(DtoBase):
    discount: Fraction
    orderId: Int32Key
    productId: Int32Key
    quantity: PositiveInt16
    unitPrice: Money
