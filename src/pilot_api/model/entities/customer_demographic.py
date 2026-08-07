from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from pilot_api.model.base import Base


class CustomerDemographic(Base):
    __tablename__ = "CustomerDemographics"

    customerTypeID: Mapped[str] = mapped_column("CustomerTypeID", String(10), primary_key=True)
    customerDesc: Mapped[str | None] = mapped_column("CustomerDesc", Text, nullable=True)
