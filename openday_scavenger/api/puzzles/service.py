from sqlalchemy.orm import Session
from segno import make
from slugify import slugify

from openday_scavenger.api.puzzles.models import Puzzle, Response

from .schemas import PuzzleCreate, PuzzleUpdate, PuzzleCompare


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

    # map the pydantic model to database model explicitly to maintain abstraction
    puzzle.name = update_data.get("name", puzzle.name)
    puzzle.active = update_data.get("active", puzzle.active)
    puzzle.answer = update_data.get("answer", puzzle.answer)
    puzzle.location = update_data.get("location", puzzle.location)
    puzzle.notes = update_data.get("notes", puzzle.notes)
    
    try:
        db_session.commit()
    except:
        db_session.rollback()
        raise

    return puzzle


def compare_answer(db_session: Session, puzzle_in: PuzzleCompare):

    puzzle = db_session.query(Puzzle).filter(Puzzle.name == puzzle_in.name).first()    

    if puzzle_in.answer == puzzle.answer:
        return True
    else:
        return False


def get_qr_code(name: str):
    return make(f"puzzles/{slugify(name)}", error='H').svg_data_uri()
    