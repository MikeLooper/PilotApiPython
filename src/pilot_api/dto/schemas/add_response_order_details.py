from pilot_api.dto.schemas.base import DtoBase


class AddResponseOrderDetailsDto(DtoBase):
    orderId: int
    productId: int
