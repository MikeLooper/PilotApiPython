from pilot_api.dto.schemas.base import DtoBase


class OrderDetailsDto(DtoBase):
    discount: float
    orderId: int
    productId: int
    quantity: int
    unitPrice: float
