from pilot_api.dto.schemas.base import DtoBase
from pilot_api.dto.schemas.fields import Int32Key


class AddResponseOrderDetailsDto(DtoBase):
    orderId: Int32Key
    productId: Int32Key
