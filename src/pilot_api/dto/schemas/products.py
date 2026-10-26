from pydantic import Field

from pilot_api.dto.schemas.base import DtoBase
from pilot_api.dto.schemas.fields import Int32Key, Money, NonNegativeInt16


class ProductsDto(DtoBase):
    categoryId: Int32Key | None = None
    discontinued: bool = False
    productId: Int32Key | None = None
    productName: str = Field(min_length=1, max_length=40)
    quantityPerUnit: str | None = Field(default=None, max_length=20)
    # An omitted value takes the database default; an explicit null is stored as null.
    reorderLevel: NonNegativeInt16 | None = 0
    supplierId: Int32Key | None = None
    unitPrice: Money | None = None
    unitsInStock: NonNegativeInt16 | None = 0
    unitsOnOrder: NonNegativeInt16 | None = 0
