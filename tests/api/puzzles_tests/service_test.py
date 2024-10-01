import pytest
from sqlalchemy.orm import Session

from openday_scavenger.api.puzzles.exceptions import PuzzleNotFoundError
from openday_scavenger.api.puzzles.schemas import PuzzleCreate
from openday_scavenger.api.puzzles.service import create, get, get_all


def test_get_all_empty(empty_db: Session) -> None:
    """
    Test the retrieval of all puzzles.

    This test retrieves all puzzles from the database and verifies that the correct number of puzzles is returned.
    As the database is empty, no puzzles should be returned.

    Args:
        empty_db (Session): The database fixture that provides an empty database.

    Asserts:
        The number of puzzles returned matches the number of puzzles created (0 in this case).
    """

    puzzles = get_all(empty_db)
    assert len(puzzles) == 0


def test_get_all(empty_db: Session) -> None:
    """
    Populate an initially empty database with one puzzle, then test the retrieval of all puzzles.

    This test retrieves all puzzles from the database and verifies that the correct number of puzzles is returned.

    Args:
        empty_db (Session): The database fixture that provides an empty database.

    Asserts:
        The number of puzzles returned matches the number of puzzles created (1 in this case).
    """
    # create a puzzle in the database
    puzzle_in = PuzzleCreate(name="demo", answer="demo", active=True)
    create(empty_db, puzzle_in=puzzle_in)

    puzzles = get_all(empty_db)
    assert len(puzzles) == 1


def test_get_all_filter(empty_db: Session) -> None:
    """
    Test the retrieval of all puzzles with a filter.

    Populate an initially empty database with multiple puzzles, then test the retrieval of all puzzles with a filter.

    Args:
        empty_db (Session): The database fixture that provides an empty database.

    Asserts:
        The number of puzzles returned with no filter matches the number of puzzles created.
        The number of puzzles returned with a filter matches the number of puzzles created that match the filter.
    """
    # create puzzles in the database
    puzzle_names = ["demo", "test", "example", "foo", "bar", "baz"]
    for _ in puzzle_names:
        create(empty_db, puzzle_in=PuzzleCreate(name=_, answer=_, active=True))

    puzzles = get_all(empty_db)
    assert len(puzzles) == len(puzzle_names)

    # filter by name one by one (querying for "start with this name" should return only one result)
    for name in puzzle_names:
        puzzles = get_all(empty_db, filter_by_name_startswith=name)
        assert len(puzzles) == 1

    # add a puzzle that shares a prefix with another puzzle
    create(empty_db, puzzle_in=PuzzleCreate(name="foo_bar", answer="foo_bar", active=True))
    puzzles = get_all(empty_db, filter_by_name_startswith="foo")
    assert len(puzzles) == 2


def test_get_all_filter_not_found(empty_db: Session) -> None:
    """
    Test the retrieval of all puzzles with a filter.

    Get all puzzles with a filter that doesn't match any puzzles.

    Args:
        empty_db (Session): The database fixture that provides an empty database.

    Asserts:
        No puzzles are returned.
    """

    # get a puzzle that doesn't exist
    puzzles = get_all(empty_db, filter_by_name_startswith="notfound")
    assert len(puzzles) == 0


def test_get_not_found(empty_db: Session) -> None:
    """
    Test the retrieval of a single puzzle that doesn't exist.

    Try to get a single puzzle, by name, that doesn't exist in the database.

    Args:
        empty_db (Session): The database fixture that provides an empty database.

    Asserts:
        A PuzzleNotFoundError is raised.
    """

    with pytest.raises(PuzzleNotFoundError):
        get(empty_db, puzzle_name="notfound")


def test_get(empty_db: Session) -> None:
    """
    Test the retrieval of a single puzzle.

    Create a puzzle in the database, then retrieve it by name.

    Args:
        empty_db (Session): The database fixture that provides an empty database.

    Asserts:
        The retrieved puzzle matches the puzzle that was created.
    """
    # create a puzzle in the database
    puzzle_in = PuzzleCreate(name="demo", answer="demo", active=True)
    create(empty_db, puzzle_in=puzzle_in)

    puzzle = get(empty_db, puzzle_name="demo")
    assert puzzle.name == puzzle_in.name
    assert puzzle.answer == puzzle_in.answer
    assert puzzle.active == puzzle_in.active
    assert puzzle.location is None
    assert puzzle.notes is None
