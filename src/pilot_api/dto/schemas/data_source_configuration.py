from pydantic import Field

from pilot_api.dto.schemas.base import DtoBase


class DataSourceConfigurationDto(DtoBase):
    active: bool = True
    connectTimeout: int | None = None
    dataSource: str | None = None
    dataSourceType: str | None = None
    host: str | None = None
    password: str | None = None
    port: int | None = None
    schema_: str | None = Field(default=None, alias="schema")
    userName: str | None = None
