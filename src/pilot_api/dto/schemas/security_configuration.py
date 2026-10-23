from pilot_api.dto.schemas.base import DtoBase


class SecurityConfigurationDto(DtoBase):
    baseUrl: str | None = None
    realm: str | None = None
    clientId: str | None = None
    requireHttpsMetadata: bool = False
    clockSkewSeconds: int = 0
    authority: str | None = None
    active: bool = True
