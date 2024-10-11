from typing import List

from pydantic import BaseModel

from openday_scavenger.api.visitors.schemas import VisitorAuth


class PuzzleCreate(BaseModel):
    id: int | None = None
    name: str
    answer: str
    active: bool = False
    location: str | None = None
    notes: str | None = None


class PuzzleUpdate(BaseModel):
    name: str | None = None
    answer: str | None = None
    active: bool | None = None
    location: str | None = None
    notes: str | None = None


class PuzzleCompare(BaseModel):
    name: str
    answer: str


class PuzzleAccess(BaseModel):
    visitor: VisitorAuth
    name: str


class ResponseTestCreate(BaseModel):
    number_visitors: int = 3000
    number_wrong_answers: int = 3


class PuzzleJson(BaseModel):
    puzzles: List[dict]
