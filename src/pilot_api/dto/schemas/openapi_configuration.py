from pilot_api.dto.schemas.base import DtoBase
from pilot_api.dto.schemas.openapi_contact_configuration import OpenApiContactConfigurationDto


class OpenApiConfigurationDto(DtoBase):
    contact: OpenApiContactConfigurationDto | None = None
    description: str | None = None
    license: str | None = None
    summary: str | None = None
    title: str | None = None
    version: str | None = None
    active: bool = True
