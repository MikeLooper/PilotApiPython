from datetime import datetime

from sqlalchemy import DateTime, Integer, LargeBinary, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from pilot_api.model.base import Base


class Employee(Base):
    __tablename__ = "Employees"

    employeeID: Mapped[int] = mapped_column(Integer, primary_key=True)
    lastName: Mapped[str | None] = mapped_column(String(255), nullable=True)
    firstName: Mapped[str | None] = mapped_column(String(255), nullable=True)
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    titleOfCourtesy: Mapped[str | None] = mapped_column(String(255), nullable=True)
    birthDate: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    hireDate: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    city: Mapped[str | None] = mapped_column(String(255), nullable=True)
    region: Mapped[str | None] = mapped_column(String(255), nullable=True)
    postalCode: Mapped[str | None] = mapped_column(String(64), nullable=True)
    country: Mapped[str | None] = mapped_column(String(255), nullable=True)
    homePhone: Mapped[str | None] = mapped_column(String(64), nullable=True)
    extension: Mapped[str | None] = mapped_column(String(64), nullable=True)
    photo: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    reportsTo: Mapped[int | None] = mapped_column(Integer, nullable=True)
    photoPath: Mapped[str | None] = mapped_column(String(512), nullable=True)
