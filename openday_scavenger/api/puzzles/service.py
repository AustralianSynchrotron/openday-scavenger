from sqlalchemy.orm import Session
from openday_scavenger.api.puzzles.models import Puzzle, Response

from .schemas import PuzzleCreate, PuzzleUpdate


def get_all(db_session: Session) -> list[Puzzle]:
    return db_session.query(Puzzle).all()


def create(db_session: Session, puzzle_in: PuzzleCreate):

    puzzle = Puzzle(
        name = puzzle_in.name,
        answer = puzzle_in.answer,
        active = puzzle_in.active,
        location = puzzle_in.location,
        notes = puzzle_in.notes
    )
    
    db_session.add(puzzle)

    try:
        db_session.commit()
    except:
        db_session.rollback()
        raise

    return puzzle


def update(db_session: Session, puzzle_in: PuzzleUpdate):
    update_data = puzzle_in.model_dump(exclude_unset=True)

    puzzle = db_session.query(Puzzle).filter(Puzzle.id == update_data["id"]).first()    

    puzzle.active = update_data.get("active", puzzle.active)

    try:
        db_session.commit()
    except:
        db_session.rollback()
        raise

    return puzzle
