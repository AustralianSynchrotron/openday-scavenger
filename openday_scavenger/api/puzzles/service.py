from pydantic import BaseModel
from sqlalchemy.orm import Session
from openday_scavenger.api.puzzles.models import Puzzle, Response

class PuzzleCreate(BaseModel):
    name: str
    answer: str
    active: bool = False
    location: str | None = None
    notes: str | None = None



def create(db_session: Session, puzzle_in: PuzzleCreate):

    puzzle = Puzzle(
        name = puzzle_in.name,
        answer = puzzle_in.answer,
        active = puzzle_in.active,
        location = puzzle_in.location,
        notes = puzzle_in.notes
    )
    
    db_session.add(puzzle)
    return puzzle