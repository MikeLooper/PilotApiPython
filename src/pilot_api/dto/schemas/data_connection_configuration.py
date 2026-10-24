from pilot_api.dto.schemas.base import DtoBase


class DataConnectionConfigurationDto(DtoBase):
    connectTimeout: int = 0
    dataSourceName: str | None = None
    host: str | None = None
    port: int | None = None
    active: bool = True
