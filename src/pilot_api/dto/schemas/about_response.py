from pilot_api.dto.schemas.application_configuration import ApplicationConfigurationDto
from pilot_api.dto.schemas.base import DtoBase


class AboutResponseDto(DtoBase):
    apiVersion: str | None = None
    applicationConfiguration: ApplicationConfigurationDto | None = None
    buildVersion: str | None = None
    deployDate: str | None = None
    name: str | None = None
