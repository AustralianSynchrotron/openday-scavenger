from datetime import datetime
from typing import List

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from openday_scavenger.api.db import Base


class Puzzle(Base):
    """Database table for a single puzzle"""

    __tablename__ = "puzzle"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(index=True, unique=True)
    answer: Mapped[str] = mapped_column(String(100))
    active: Mapped[bool] = mapped_column(default=False)
    location: Mapped[str] = mapped_column(String(200), nullable=True)
    notes: Mapped[str] = mapped_column(nullable=True)

    responses: Mapped[List["Response"]] = relationship(back_populates="puzzle")

    def __repr__(self) -> str:
        return f"Puzzle(id={self.id!r}, name={self.name!r}, answer={self.answer!r})"


class Response(Base):
    """Database table to record every answer for every visitor"""

    __tablename__ = "response"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    visitor_id: Mapped[int] = mapped_column(ForeignKey("visitor.id"))
    puzzle_id: Mapped[int] = mapped_column(ForeignKey("puzzle.id"))
    answer: Mapped[str] = mapped_column(String(100))
    is_correct: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column()

    visitor: Mapped["Visitor"] = relationship(back_populates="responses")  # noqa F821 # type: ignore
    puzzle: Mapped["Puzzle"] = relationship(back_populates="responses")

    def __repr__(self) -> str:
        return (
            f"Response("
            f"id={self.id!r}, visitor={self.visitor_id!r}, puzzle={self.puzzle_id!r},"
            f"answer={self.answer!r}, correct={self.is_correct!r})"
        )
