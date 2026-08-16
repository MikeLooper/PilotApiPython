from pydantic import field_validator

from pilot_api.dto.schemas.base import DtoBase, coerce_number


class CategoriesDto(DtoBase):
    categoryID: int | None = None
    categoryName: str | None
    description: str | None = None
    picture: str | None = None

    @field_validator("categoryID", mode="before")
    @classmethod
    def validate_category_id(cls, value: object) -> object:
        return coerce_number(value)
