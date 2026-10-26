from pydantic import Field

from pilot_api.dto.schemas.base import DtoBase
from pilot_api.dto.schemas.fields import Int32Key


class ShippersDto(DtoBase):
    companyName: str = Field(min_length=1, max_length=40)
    phone: str | None = Field(default=None, max_length=24)
    shipperId: Int32Key | None = None
