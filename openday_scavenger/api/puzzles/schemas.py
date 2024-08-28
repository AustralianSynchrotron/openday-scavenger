from pydantic import BaseModel


class PuzzleCreate(BaseModel):
    name: str
    answer: str
    active: bool = False
    location: str | None = None
    notes: str | None = None


class PuzzleUpdate(BaseModel):
    id: int
    name: str | None = None
    answer: str | None = None
    active: bool | None = None
    location: str | None = None
    notes: str | None = None


class PuzzleRead(BaseModel):
    id: int
    name: str
    answer: str
    active: bool
    location: str | None
    notes: str | None
