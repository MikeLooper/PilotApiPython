from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from pilot_api.model.base import Base


class CustomerCustomerDemo(Base):
    __tablename__ = "CustomerCustomerDemo"

    customerID: Mapped[str] = mapped_column("CustomerID", String(5), primary_key=True)
    customerTypeID: Mapped[str] = mapped_column("CustomerTypeID", String(10), primary_key=True)
