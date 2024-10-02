import random
from datetime import datetime
from io import BytesIO

from sqlalchemy.orm import Session

from openday_scavenger.api.puzzles.models import Access, Puzzle, Response
from openday_scavenger.api.qr_codes import generate_qr_code, generate_qr_codes_pdf
from openday_scavenger.api.visitors.exceptions import VisitorUIDInvalidError
from openday_scavenger.api.visitors.models import Visitor
from openday_scavenger.api.visitors.schemas import VisitorPoolCreate
from openday_scavenger.api.visitors.service import create_visitor_pool, get_visitor_pool
from openday_scavenger.config import get_settings

from .exceptions import (
    AccessCreationError,
    ForbiddenAccessTestEndpointError,
    PuzzleCreationError,
    PuzzleNotFoundError,
    PuzzleUpdatedError,
)
from .schemas import PuzzleCompare, PuzzleCreate, PuzzleUpdate

__all__ = (
    "get_all",
    "count",
    "get_all_responses",
    "create",
    "update",
    "compare_answer",
    "record_access",
    "generate_puzzle_qr_code",
    "generate_puzzle_qr_codes_pdf",
    "generate_test_data",
)


config = get_settings()


def get_all(
    db_session: Session,
    *,
    only_active: bool = False,
    filter_by_name_startswith: str | None = None,
) -> list[Puzzle]:
    """
    Return all puzzles in the database, with optional filtering.
    optionally only the active ones.

    Args:
        db_session (Session): The SQLAlchemy session object.
        only_active (bool): Set this to True to only return active puzzles.
        filter_by_name_startswith (str): Only return responses
            where the puzzle name starts with this string.

    Returns:
        list[Puzzle]: List of puzzles in the database.
    """
    # Construct the database query dynamically, taking into account
    # whether only active puzzles should be returned.
    q = db_session.query(Puzzle)

    if only_active:
        q = q.filter(Puzzle.active)

    if (filter_by_name_startswith is not None) and (filter_by_name_startswith != ""):
        q = q.filter(Puzzle.name.ilike(f"{filter_by_name_startswith}%"))

    return q.order_by(Puzzle.name).all()


def get(db_session: Session, puzzle_name: str) -> Puzzle:
    """
    Return a single puzzle from the database.

    Args:
        db_session (Session): The SQLAlchemy session object.
        puzzle_name (str): The name of the puzzle that should be returned.

    Returns:
        Puzzle: The puzzle with the given name.
    """
    # Get the puzzle from the database with the provided name.
    puzzle = db_session.query(Puzzle).filter(Puzzle.name == puzzle_name).first()

    if puzzle is None:
        raise PuzzleNotFoundError(
            f"A puzzle with the name {puzzle_name} could not be found in the database"
        )

    return puzzle


def count(db_session: Session, *, only_active: bool = False) -> int:
    """
    Convenience method to count the number of puzzles.

    Args:
        db_session (Session): The SQLAlchemy session object.
        only_active (bool): Set this to True to only count active puzzles.

    Returns:
        int: The number of puzzles.
    """
    # Construct the database query dynamically, taking into account
    # whether only active puzzles should be counted.
    q = db_session.query(Puzzle)

    if only_active:
        q = q.filter(Puzzle.active)

    return q.count()


def get_all_responses(
    db_session: Session,
    *,
    filter_by_puzzle_name: str | None = None,
    filter_by_visitor_uid: str | None = None,
) -> list[Response]:
    """
    Return all puzzle responses in the database with optional filtering.

    Args:
        db_session (Session): The SQLAlchemy session object.
        filter_by_puzzle_name (str): Only return responses where
                                        the puzzle name starts with this string.
        filter_by_visitor_uid (str): Only return responses where
                                        the visitor uid starts with this string.

    Returns:
        list[Response]: List of responses with the filters applied.
    """
    # Construct the database query dynamically. If the result needs to be filtered
    # by the first letters of the puzzle name or visitor uid, join the tables first
    # before applying the filter. We use ilike here, so the filter is case-insensitive.
    q = db_session.query(Response)

    if (filter_by_puzzle_name is not None) and (filter_by_puzzle_name != ""):
        q = q.join(Response.puzzle).filter(Puzzle.name.ilike(f"{filter_by_puzzle_name}%"))

    if (filter_by_visitor_uid is not None) and (filter_by_visitor_uid != ""):
        q = q.join(Response.visitor).filter(Visitor.uid.ilike(f"{filter_by_visitor_uid}%"))

    return q.all()


def create(db_session: Session, puzzle_in: PuzzleCreate) -> Puzzle:
    """
    Create a new puzzle entry in the database and return the entry.

    Args:
        db_session (Session): The SQLAlchemy session object.
        puzzle_in (PuzzleCreate): The object containing the data for the creation of a puzzle.

    Returns:
        Puzzle: The created puzzle.
    """
    # Create the database model object and pass in the pydantic schema values
    # explicitly. This maintains a nice abstraction between the service layer
    # and the database layer.
    puzzle = Puzzle(
        name=puzzle_in.name,
        answer=puzzle_in.answer,
        active=puzzle_in.active,
        location=puzzle_in.location,
        notes=puzzle_in.notes,
    )

    # Attempt adding the entry to the database. If it fails, roll back.
    try:
        db_session.add(puzzle)
        db_session.commit()
    except Exception:
        db_session.rollback()
        raise PuzzleCreationError(f"Failed to create the puzzle {puzzle_in.name}")

    return puzzle


def update(db_session: Session, puzzle_name: str, puzzle_in: PuzzleUpdate) -> Puzzle:
    """
    Update a puzzle entry in the database and return the updated entry.

    Args:
        db_session (Session): The SQLAlchemy session object.
        puzzle_name (str): The name of the puzzle that should be updated.
        puzzle_in (PuzzleUpdate): The object containing the fields and values that should be changed.

    Returns:
        Puzzle: The modified puzzle.
    """
    # Find the puzzle that should be updated in the database
    puzzle = get(db_session, puzzle_name)

    # We transform the input data which contains the fields with the new values
    # to a dictionary and in the process filter out any fields that have not been explicitly set.
    # This means any field in the pydantic model that has either not been touched or
    # has been assigned the default value is ignored.
    update_data = puzzle_in.model_dump(exclude_unset=True)

    # We map the pydantic model to the database model explicitly in order to maintain abstraction.
    puzzle.name = update_data.get("name", puzzle.name)
    puzzle.active = update_data.get("active", puzzle.active)
    puzzle.answer = update_data.get("answer", puzzle.answer)
    puzzle.location = update_data.get("location", puzzle.location)
    puzzle.notes = update_data.get("notes", puzzle.notes)

    # Attempt modifying the entry in the database. If it fails, roll back.
    try:
        db_session.commit()
    except Exception:
        db_session.rollback()
        raise PuzzleUpdatedError(f"Failed to update the puzzle {puzzle_name}")

    return puzzle


def compare_answer(db_session: Session, puzzle_in: PuzzleCompare) -> bool:
    """
    Compare the provided answer with the stored answer and return whether it is correct.

    Args:
        db_session (Session): The SQLAlchemy session object.
        puzzle_in (PuzzleCompare): The object containing the visitor's answer that should be compared.
    """
    # Get the database models for the puzzle so we can perform the answer comparison.
    puzzle = get(db_session, puzzle_in.name)

    # We compare the provided answer with the stored answer. Currently this is a very simple
    # case sensitive string comparison. We can add more complicated comparison modes here later.
    is_correct = puzzle_in.answer == puzzle.answer

    # If the session management is turned off, skip the creation and storage
    # of a response as it is connected to a visitor uid.
    if config.SESSIONS_ENABLED:
        # Get the database model for the visitor so we can record who submitted the answer in the response table.
        visitor = db_session.query(Visitor).filter(Visitor.uid == puzzle_in.visitor).first()

        if visitor is None:
            raise VisitorUIDInvalidError(
                f"Could not find visitor {puzzle_in.visitor} in the database."
            )

        # Create a new response entry and store it in the database
        response = Response(
            visitor=visitor,
            puzzle=puzzle,
            answer=puzzle_in.answer,
            is_correct=is_correct,
            created_at=datetime.now(),
        )

        # Attempt adding the entry to the database. If it fails, roll back.
        try:
            db_session.add(response)
            db_session.commit()
        except:
            db_session.rollback()
            raise

    return is_correct


def record_access(db_session: Session, puzzle_name: str, visitor_uid: str) -> Access:
    """
    Record that a visitor has accessed a puzzle.

    Args:
        db_session (Session): The SQLAlchemy session object.
        puzzle_name (str): The name of the puzzle the visitor accessed.
        visitor_uid (str): The uid of the visitor that accessed the puzzle.

    Returns:
        Access: The created access object.
    """
    # Get the database models for the puzzle.
    puzzle = get(db_session, puzzle_name)

    # Get the database model for the visitor.
    visitor = db_session.query(Visitor).filter(Visitor.uid == visitor_uid).first()

    if visitor is None:
        raise VisitorUIDInvalidError(f"Could not find visitor {visitor_uid} in the database.")

    access = Access(
        puzzle=puzzle,
        visitor=visitor,
        created_at=datetime.now(),
    )

    # Attempt adding the entry to the database. If it fails, roll back.
    try:
        db_session.add(access)
        db_session.commit()
    except Exception:
        db_session.rollback()
        raise AccessCreationError(f"Could not record the access to {puzzle_name} by {visitor_uid}")

    return access


def generate_puzzle_qr_code(name: str, as_file_buff: bool = False) -> str | BytesIO:
    return generate_qr_code(f"puzzles/{name}", as_file_buff=as_file_buff)


def generate_puzzle_qr_codes_pdf(db_session: Session):
    puzzles = get_all(db_session, only_active=False)

    return generate_qr_codes_pdf([puzzle.name for puzzle in puzzles])


def generate_test_data(
    db_session: Session, *, number_visitors: int = 3000, number_wrong_answers: int = 3
):
    """
    Generate random test data in the database.

    Use very carefully and not in production. This is meant for performance tests.
    It will take a while to generate all the test data.

    Args:
        db_session (Session): The SQLAlchemy session object.
        number_visitors (int): The number of visitors that should be generated
        number_wrong_answers (int): The number of wrong answers that should be
                                    generated for each visitor and each puzzle.

    """
    if not config.TEST_ENDPOINT_ENABLED:
        raise ForbiddenAccessTestEndpointError("Not allowed to access this endpoint")

    # Create a pool of visitors using the provided number of visitors
    create_visitor_pool(db_session, VisitorPoolCreate(number_of_entries=number_visitors))

    visitors_pool = get_visitor_pool(db_session, limit=number_visitors)
    puzzles = get_all(db_session, only_active=True)

    # Loop over all visitors from the pool, add them to the visitor table and
    # generate a number of responses for each puzzle.
    try:
        for visitor_from_pool in visitors_pool:
            visitor = Visitor(uid=visitor_from_pool.uid, checked_in=datetime.now())
            db_session.add(visitor)
            db_session.delete(visitor_from_pool)

            for puzzle in puzzles:
                # Add the wrong answers
                for _ in range(number_wrong_answers):
                    response = Response(
                        visitor=visitor,
                        puzzle=puzzle,
                        answer="wrong answer",
                        is_correct=False,
                        created_at=datetime.now(),
                    )
                    db_session.add(response)

                # Randomly add a correct Answer
                if random.randint(1, 3) < 3:
                    response = Response(
                        visitor=visitor,
                        puzzle=puzzle,
                        answer=puzzle.answer,
                        is_correct=True,
                        created_at=datetime.now(),
                    )
                    db_session.add(response)

            # commit for each visitor
            db_session.commit()
    except:
        db_session.rollback()
        raise
