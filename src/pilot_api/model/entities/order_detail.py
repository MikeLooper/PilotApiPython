from sqlalchemy import Integer, SmallInteger
from sqlalchemy.orm import Mapped, mapped_column

from pilot_api.model.base import Base
from pilot_api.model.types import CrossDatabaseFloat


class OrderDetail(Base):
    __tablename__ = "Order Details"

    orderID: Mapped[int] = mapped_column(Integer, primary_key=True)
    productID: Mapped[int] = mapped_column(Integer, primary_key=True)
    unitPrice: Mapped[float] = mapped_column(CrossDatabaseFloat, nullable=False)
    quantity: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    discount: Mapped[float] = mapped_column(CrossDatabaseFloat, nullable=False)
