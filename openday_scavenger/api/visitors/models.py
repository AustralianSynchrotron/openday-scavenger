from datetime import datetime
from typing import List

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import String

from openday_scavenger.api.db import Base


class Visitor(Base):
    """Database table for a single visitor"""

    __tablename__ = "visitor"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    uid: Mapped[str] = mapped_column(String(6), index=True, unique=True)
    checked_in: Mapped[datetime] = mapped_column()
    checked_out: Mapped[datetime | None] = mapped_column(nullable=True, default=None)

    responses: Mapped[List["Response"]] = relationship(back_populates="visitor")  # noqa F821 # type: ignore

    def __repr__(self) -> str:
        return f"Visitor(id={self.id!r}, uid={self.uid!r})"


class VisitorPool(Base):
    __tablename__ = "visitor_pool"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    uid: Mapped[str] = mapped_column(String(6), index=True, unique=True)
