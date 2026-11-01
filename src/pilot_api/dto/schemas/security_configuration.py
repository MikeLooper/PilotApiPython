from pilot_api.dto.schemas.base import DtoBase
from pilot_api.dto.schemas.fields import Int32


class SecurityConfigurationDto(DtoBase):
    baseUrl: str | None = None
    realm: str | None = None
    clientId: str | None = None
    requireHttpsMetadata: bool = False
    clockSkewSeconds: Int32 = 0
    authority: str | None = None
    active: bool = True
