from pydantic import Field

from pilot_api.dto.schemas.base import DtoBase


class DataSourceConfigurationDto(DtoBase):
    dataSource: str | None = None
    dataSourceEnum: int | None = None
    dataSourceName: str | None = None
    dataSourceType: str | None = None
    schema_: str | None = Field(default=None, alias="schema")
    active: bool = True
