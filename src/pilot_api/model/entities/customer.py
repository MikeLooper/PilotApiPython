from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from pilot_api.model.base import Base


class Customer(Base):
    __tablename__ = "Customers"

    customerID: Mapped[str] = mapped_column(String(32), primary_key=True)
    companyName: Mapped[str | None] = mapped_column(String(255), nullable=True)
    contactName: Mapped[str | None] = mapped_column(String(255), nullable=True)
    contactTitle: Mapped[str | None] = mapped_column(String(255), nullable=True)
    address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    city: Mapped[str | None] = mapped_column(String(255), nullable=True)
    region: Mapped[str | None] = mapped_column(String(255), nullable=True)
    postalCode: Mapped[str | None] = mapped_column(String(64), nullable=True)
    country: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(64), nullable=True)
    fax: Mapped[str | None] = mapped_column(String(64), nullable=True)
