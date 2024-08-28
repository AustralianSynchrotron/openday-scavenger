from datetime import datetime
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from openday_scavenger.api.db import Base


class Puzzle(Base):
    __tablename__ = "puzzle"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(index=True, unique=True)
    answer: Mapped[str] = mapped_column(String(100))
    active: Mapped[bool] = mapped_column(default=False)
    location: Mapped[str] = mapped_column(String(200), nullable=True)
    notes: Mapped[str]= mapped_column(nullable=True)

    def __repr__(self) -> str:
        return f"Puzzle(id={self.id!r}, name={self.name!r}, answer={self.answer!r})"


class Response(Base):
    __tablename__ = "response"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    visitor_id: Mapped[int] = mapped_column(ForeignKey("visitor.id"))
    puzzle_id: Mapped[int] = mapped_column(ForeignKey("puzzle.id"))
    answer: Mapped[str] = mapped_column(String(100))
    correct: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column()

    def __repr__(self) -> str:
        return f"Response(id={self.id!r}, visitor={self.visitor_id!r}, puzzle={self.puzzle_id!r}, answer={self.answer!r}, correct={self.correct!r})"
