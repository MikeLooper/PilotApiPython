from sqlalchemy import Integer, LargeBinary, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from pilot_api.model.base import Base


class Category(Base):
    __tablename__ = "Categories"

    categoryID: Mapped[int] = mapped_column(Integer, primary_key=True)
    categoryName: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    picture: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
