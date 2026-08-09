from sqlalchemy import Boolean, Float, Integer, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from pilot_api.model.base import Base


class Product(Base):
    __tablename__ = "Products"

    productID: Mapped[int] = mapped_column(Integer, primary_key=True)
    productName: Mapped[str | None] = mapped_column(String(255), nullable=True)
    supplierID: Mapped[int | None] = mapped_column(Integer, nullable=True)
    categoryID: Mapped[int | None] = mapped_column(Integer, nullable=True)
    quantityPerUnit: Mapped[str | None] = mapped_column(String(255), nullable=True)
    unitPrice: Mapped[float | None] = mapped_column(Float, nullable=True)
    unitsInStock: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    unitsOnOrder: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    reorderLevel: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    discontinued: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
