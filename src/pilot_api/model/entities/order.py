from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from pilot_api.model.base import Base
from pilot_api.model.types import CrossDatabaseFloat


class Order(Base):
    __tablename__ = "Orders"

    orderID: Mapped[int] = mapped_column(Integer, primary_key=True)
    customerID: Mapped[str | None] = mapped_column(String(32), nullable=True)
    employeeID: Mapped[int | None] = mapped_column(Integer, nullable=True)
    orderDate: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    requiredDate: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    shippedDate: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    shipVia: Mapped[int | None] = mapped_column(Integer, nullable=True)
    freight: Mapped[float | None] = mapped_column(CrossDatabaseFloat, nullable=True)
    shipName: Mapped[str | None] = mapped_column(String(255), nullable=True)
    shipAddress: Mapped[str | None] = mapped_column(String(255), nullable=True)
    shipCity: Mapped[str | None] = mapped_column(String(255), nullable=True)
    shipRegion: Mapped[str | None] = mapped_column(String(255), nullable=True)
    shipPostalCode: Mapped[str | None] = mapped_column(String(64), nullable=True)
    shipCountry: Mapped[str | None] = mapped_column(String(255), nullable=True)
