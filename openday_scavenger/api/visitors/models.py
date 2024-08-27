from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from ..db import Base

class Visitor(Base):
    __tablename__ = "visitor"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    uuid: Mapped[UUID] = mapped_column(index=True)
    checked_in: Mapped[datetime] = mapped_column()
    checked_out: Mapped[datetime | None] = mapped_column(default=None)

    def __repr__(self) -> str:
        return f"Visitor(id={self.id!r}, uuid={self.uuid!r})"
