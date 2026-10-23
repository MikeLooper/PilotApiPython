from pilot_api.dto.schemas.base import DtoBase


class ProductsDto(DtoBase):
    categoryId: int | None = None
    discontinued: bool = False
    productId: int | None = None
    productName: str | None
    quantityPerUnit: str | None = None
    reorderLevel: int = 0
    supplierId: int | None = None
    unitPrice: float | None = None
    unitsInStock: int = 0
    unitsOnOrder: int = 0
