from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from pilot_api.model.base import Base


class Territory(Base):
    __tablename__ = "Territories"

    territoryID: Mapped[str] = mapped_column("TerritoryID", String(20), primary_key=True)
    territoryDescription: Mapped[str] = mapped_column("TerritoryDescription", String(50), nullable=False)
    regionID: Mapped[int] = mapped_column("RegionID", Integer, nullable=False)
