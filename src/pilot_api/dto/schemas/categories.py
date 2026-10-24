from pydantic import Field

from pilot_api.dto.schemas.base import DtoBase


class CategoriesDto(DtoBase):
    categoryId: int | None = None
    categoryName: str | None
    description: str | None = None
    picture: str | None = Field(default=None, json_schema_extra={"format": "byte"})
