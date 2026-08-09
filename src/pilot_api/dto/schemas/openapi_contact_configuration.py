from pilot_api.dto.schemas.base import DtoBase


class OpenApiContactConfigurationDto(DtoBase):
    email: str | None = None
    name: str | None = None
    url: str | None = None
    active: bool = True
