from pydantic import Field

from pilot_api.dto.schemas.base import DtoBase
from pilot_api.dto.schemas.data_source_types import DataSourceTypes


class DataSourceConfigurationDto(DtoBase):
    dataSource: str | None = None
    dataSourceEnum: DataSourceTypes = DataSourceTypes.UNRECOGNIZED
    dataSourceName: str | None = None
    dataSourceType: str | None = None
    schema_: str | None = Field(default=None, alias="schema")
    active: bool = True
