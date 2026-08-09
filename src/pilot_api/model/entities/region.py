from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from pilot_api.model.base import Base


class Region(Base):
    __tablename__ = "Region"

    regionID: Mapped[int] = mapped_column("RegionID", Integer, primary_key=True)
    regionDescription: Mapped[str] = mapped_column("RegionDescription", String(50), nullable=False)
