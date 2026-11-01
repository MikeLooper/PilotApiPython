from pilot_api.dto.schemas.base import DtoBase
from pilot_api.dto.schemas.fields import Int32


class OpenTelemetryConfigurationDto(DtoBase):
    port: Int32 | None = None
    server: str | None = None
    active: bool = True
