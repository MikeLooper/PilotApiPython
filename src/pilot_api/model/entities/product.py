from sqlalchemy import Boolean, Integer, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from pilot_api.model.base import Base
from pilot_api.model.types import CrossDatabaseFloat


class Product(Base):
    __tablename__ = "Products"

    productId: Mapped[int] = mapped_column("productID", Integer, primary_key=True)
    productName: Mapped[str | None] = mapped_column(String(255), nullable=True)
    supplierId: Mapped[int | None] = mapped_column("supplierID", Integer, nullable=True)
    categoryId: Mapped[int | None] = mapped_column("categoryID", Integer, nullable=True)
    quantityPerUnit: Mapped[str | None] = mapped_column(String(255), nullable=True)
    unitPrice: Mapped[float | None] = mapped_column(CrossDatabaseFloat, nullable=True)
    unitsInStock: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    unitsOnOrder: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    reorderLevel: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    discontinued: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
