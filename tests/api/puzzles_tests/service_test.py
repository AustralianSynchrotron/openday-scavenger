from sqlalchemy.orm import Session

from openday_scavenger.api.puzzles.schemas import PuzzleCreate
from openday_scavenger.api.puzzles.service import create, get_all


def test_get_all_empty(empty_db: Session) -> None:
    """
    Test the retrieval of all puzzles.

    This test retrieves all puzzles from the database and verifies that the correct number of puzzles is returned.

    Args:
        empty_db (Session): The database fixture that provides an empty database.

    Asserts:
        The number of puzzles returned matches the number of puzzles created.
    """

    puzzles = get_all(empty_db)
    assert len(puzzles) == 0


def test_get_all(empty_db: Session) -> None:
    # create a puzzle in the database
    puzzle_in = PuzzleCreate(name="demo", answer="demo", active=True)
    create(empty_db, puzzle_in=puzzle_in)

    puzzles = get_all(empty_db)
    assert len(puzzles) == 1
