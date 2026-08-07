from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from pilot_api.model.base import Base


class EmployeeTerritory(Base):
    __tablename__ = "EmployeeTerritories"

    employeeID: Mapped[int] = mapped_column("EmployeeID", Integer, primary_key=True)
    territoryID: Mapped[str] = mapped_column("TerritoryID", String(20), primary_key=True)
