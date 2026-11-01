from pilot_api.dto.schemas.base import DtoBase
from pilot_api.dto.schemas.fields import Int32Key


class AddResponseIntDto(DtoBase):
    id: Int32Key
