from pilot_api.dto.schemas.base import DtoBase
from pilot_api.dto.schemas.data_connection_configuration import DataConnectionConfigurationDto
from pilot_api.dto.schemas.data_source_configuration import DataSourceConfigurationDto
from pilot_api.dto.schemas.openapi_configuration import OpenApiConfigurationDto


class ApplicationConfigurationDto(DtoBase):
    dataConnections: list[DataConnectionConfigurationDto] | None = None
    dataSources: list[DataSourceConfigurationDto] | None = None
    openApi: OpenApiConfigurationDto | None = None
    active: bool = True
