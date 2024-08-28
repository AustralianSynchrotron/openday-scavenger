from datetime import datetime
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.types import String
from openday_scavenger.api.db import Base


class Visitor(Base):
    __tablename__ = "visitor"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    uid: Mapped[str] = mapped_column(String(6), index=True, unique=True)
    checked_in: Mapped[datetime] = mapped_column()
    checked_out: Mapped[datetime | None] = mapped_column(nullable=True, default=None)

    def __repr__(self) -> str:
        return f"Visitor(id={self.id!r}, uid={self.uid!r})"
