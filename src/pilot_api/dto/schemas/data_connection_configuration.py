from pilot_api.dto.schemas.base import DtoBase


class DataConnectionConfigurationDto(DtoBase):
    connectTimeout: int | None = None
    dataSourceName: str | None = None
    host: str | None = None
    password: str | None = None
    port: int | None = None
    userName: str | None = None
    active: bool = True
