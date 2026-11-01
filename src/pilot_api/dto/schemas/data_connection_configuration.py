from pilot_api.dto.schemas.base import DtoBase
from pilot_api.dto.schemas.fields import Int32


class DataConnectionConfigurationDto(DtoBase):
    connectTimeout: Int32 = 0
    dataSourceName: str | None = None
    host: str | None = None
    port: Int32 | None = None
    active: bool = True
