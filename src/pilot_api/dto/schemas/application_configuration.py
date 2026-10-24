from pilot_api.dto.schemas.base import DtoBase
from pilot_api.dto.schemas.data_connection_configuration import DataConnectionConfigurationDto
from pilot_api.dto.schemas.data_source_configuration import DataSourceConfigurationDto
from pilot_api.dto.schemas.open_telemetry_configuration import OpenTelemetryConfigurationDto
from pilot_api.dto.schemas.openapi_configuration import OpenApiConfigurationDto
from pilot_api.dto.schemas.security_configuration import SecurityConfigurationDto


class ApplicationConfigurationDto(DtoBase):
    dataConnections: list[DataConnectionConfigurationDto] | None = None
    dataSources: list[DataSourceConfigurationDto] | None = None
    security: SecurityConfigurationDto | None = None
    openApi: OpenApiConfigurationDto | None = None
    openTelemetry: OpenTelemetryConfigurationDto | None = None
    active: bool = True
