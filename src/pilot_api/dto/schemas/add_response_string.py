from pydantic import ConfigDict

from pilot_api.dto.schemas.base import DtoBase, omit_required
from pilot_api.dto.schemas.fields import StringKey


class AddResponseStringDto(DtoBase):
    # Always returned, but the shared definition does not list id as required.
    model_config = ConfigDict(json_schema_extra=omit_required)

    id: StringKey
