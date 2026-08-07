from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from pilot_api.model.base import Base


class Shipper(Base):
    __tablename__ = "Shippers"

    shipperID: Mapped[int] = mapped_column(Integer, primary_key=True)
    companyName: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(64), nullable=True)
