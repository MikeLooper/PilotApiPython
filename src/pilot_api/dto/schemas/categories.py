from pydantic import Field

from pilot_api.dto.schemas.base import DtoBase
from pilot_api.dto.schemas.fields import Int32Key


class CategoriesDto(DtoBase):
    categoryId: Int32Key | None = None
    categoryName: str = Field(min_length=1, max_length=15)
    description: str | None = None
    picture: str | None = Field(default=None, json_schema_extra={"format": "byte"})
