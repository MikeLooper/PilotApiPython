from pydantic import field_validator

from pilot_api.dto.schemas.base import DtoBase, coerce_number


class ProductsDto(DtoBase):
    categoryID: int | None = None
    discontinued: bool
    productID: int | None = None
    productName: str | None
    quantityPerUnit: str | None = None
    reorderLevel: int
    supplierID: int | None = None
    unitPrice: float | None = None
    unitsInStock: int
    unitsOnOrder: int

    @field_validator(
        "productID",
        "supplierID",
        "categoryID",
        "unitPrice",
        "unitsInStock",
        "unitsOnOrder",
        "reorderLevel",
        mode="before",
    )
    @classmethod
    def validate_product_numbers(cls, value: object) -> object:
        return coerce_number(value)
