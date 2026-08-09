from pilot_api.dto.schemas.base import DtoBase


class CustomerDemographicsDto(DtoBase):
    customerTypeID: str
    customerDesc: str | None = None
