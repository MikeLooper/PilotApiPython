from pilot_api.dto.schemas.base import DtoBase


class OpenTelemetryConfigurationDto(DtoBase):
    port: int | None = None
    server: str | None = None
    active: bool = True
