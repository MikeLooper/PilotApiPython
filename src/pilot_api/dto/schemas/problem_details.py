from pilot_api.dto.schemas.base import DtoBase


class ProblemDetailsDto(DtoBase):
    type: str | None = None
    title: str | None = None
    status: int | None = None
    detail: str | None = None
    instance: str | None = None
