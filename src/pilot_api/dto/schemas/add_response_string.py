from pilot_api.dto.schemas.base import DtoBase
from pilot_api.dto.schemas.fields import StringKey


class AddResponseStringDto(DtoBase):
    id: StringKey
