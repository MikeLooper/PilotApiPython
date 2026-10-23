from pilot_api.dto.schemas.base import DtoBase


class ShippersDto(DtoBase):
    companyName: str | None = None
    phone: str | None = None
    shipperId: int | None = None
