import json
import random
from datetime import datetime, timedelta
from io import BytesIO
from pathlib import Path
from sys import modules
from typing import Any

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from openday_scavenger.api.puzzles.exceptions import (
    PuzzleStateCreationError,
    PuzzleStateUpdatedError,
)
from openday_scavenger.api.puzzles.models import Access, Puzzle, Response, State
from openday_scavenger.api.qr_codes import generate_qr_code, generate_qr_codes_pdf
from openday_scavenger.api.visitors.exceptions import VisitorUIDInvalidError
from openday_scavenger.api.visitors.models import Visitor
from openday_scavenger.api.visitors.schemas import VisitorAuth, VisitorPoolCreate
from openday_scavenger.api.visitors.service import create_visitor_pool, get_visitor_pool
from openday_scavenger.config import get_settings

from .exceptions import (
    AccessCreationError,
    ForbiddenAccessTestEndpointError,
    PuzzleCreationError,
    PuzzleNotFoundError,
    PuzzleUpdatedError,
)
from .schemas import PuzzleCreate, PuzzleJson, PuzzleUpdate

__all__ = (
    "get_all",
    "get",
    "count",
    "get_all_responses",
    "count_responses",
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


def count_responses(db_session: Session, *, only_correct: bool = False) -> int:
    """
    Convenience method to count the number of responses.

    Args:
        db_session (Session): The SQLAlchemy session object.
        only_correct (bool): Set this to True to only count correct responses.

    Returns:
        int: The number of responses.
    """
    # Construct the database query dynamically, taking into account
    # whether only correct responses should be counted.
    q = db_session.query(Response)

    if only_correct:
        q = q.filter(Response.is_correct)

    return q.count()


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


def compare_answer(
    db_session: Session, *, puzzle_name: str, visitor_auth: VisitorAuth, answer: str
) -> bool:
    """
    Compare the provided answer with the stored answer and return whether it is correct.

    Args:
        db_session (Session): The SQLAlchemy session object.
        puzzle_name (str): The name of the puzzle against which the answer should be checked.
        visitor_auth (VisitorAuth): The authenticated visitor that accessed the puzzle.
        answer (str): The answer the visitor gave for the puzzle.

    Returns:
        bool: Returns true of the answer was correct.
    """
    # Get the database models for the puzzle so we can perform the answer comparison.
    puzzle = get(db_session, puzzle_name)

    # We compare the provided answer with the stored answer. Currently this is a very simple
    # case sensitive string comparison. We can add more complicated comparison modes here later.
    is_correct = answer.strip().lower() == puzzle.answer.lower()

    # Only store the response if the visitor is active (not None and authenticated)
    if visitor_auth.is_active:
        # Get the database model for the visitor so we can record who submitted the answer in the response table.
        visitor = db_session.query(Visitor).filter(Visitor.uid == visitor_auth.uid).first()

        if visitor is None:
            raise VisitorUIDInvalidError(
                f"Could not find visitor {visitor_auth.uid} in the database."
            )

        # Create a new response entry and store it in the database
        response = Response(
            visitor=visitor,
            puzzle=puzzle,
            answer=answer,
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


def record_access(
    db_session: Session, *, puzzle_name: str, visitor_auth: VisitorAuth
) -> Access | None:
    """
    Record that a visitor has accessed a puzzle.

    Args:
        db_session (Session): The SQLAlchemy session object.
        puzzle_name (str): The name of the puzzle the visitor accessed.
        visitor_auth (VisitorAuth): The authenticated visitor that accessed the puzzle.

    Returns:
        Access: The created access object or None if no Access object was created.
    """
    # Only record the access if the visitor is active
    # (authenticated and the registration system is enabled)
    if not visitor_auth.is_active:
        return

    # Get the database models for the puzzle.
    puzzle = get(db_session, puzzle_name)

    # Get the database model for the visitor.
    visitor = db_session.query(Visitor).filter(Visitor.uid == visitor_auth.uid).first()

    if visitor is None:
        raise VisitorUIDInvalidError(f"Could not find visitor {visitor_auth.uid} in the database.")

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
        raise AccessCreationError(
            f"Could not record the access to {puzzle_name} by {visitor_auth.uid}"
        )

    return access


def get_puzzle_state(
    db_session: Session, *, puzzle_name: str, visitor_auth: VisitorAuth
) -> dict[str, Any]:
    """
    Get the state information for the given puzzle and visitor.

    Args:
        db_session (Session): The SQLAlchemy session object.
        puzzle_name (str): The name of the puzzle the visitor accessed.
        visitor_auth (VisitorAuth): The authenticated visitor that accessed the puzzle.

    Returns:
        dict[str, Any]: The state as a dictionary that the puzzle can structure as it sees fit.
    """
    # Puzzle states only work if there is a valid and authenticated visitor
    if not visitor_auth.is_active:
        return {}

    # Get the database model for the visitor.
    visitor = db_session.query(Visitor).filter(Visitor.uid == visitor_auth.uid).first()
    if visitor is None:
        raise VisitorUIDInvalidError(f"Could not find visitor {visitor_auth.uid} in the database.")

    # Get the database models for the puzzle.
    puzzle = get(db_session, puzzle_name)

    # Check whether a state for the puzzle and visitor already exists.
    state_model = (
        db_session.query(State)
        .filter(State.puzzle_id == puzzle.id, State.visitor_id == visitor.id)
        .first()
    )

    if state_model is None:
        return {}
    else:
        return json.loads(state_model.state)


def set_puzzle_state(
    db_session: Session, *, puzzle_name: str, visitor_auth: VisitorAuth, state: dict[str, Any]
):
    """
    Set the state information for the given puzzle and visitor.

    Args:
        db_session (Session): The SQLAlchemy session object.
        puzzle_name (str): The name of the puzzle the visitor accessed.
        visitor_auth (VisitorAuth): The authenticated visitor that accessed the puzzle.
        state (dict[str, Any]): The state as a dictionary that the puzzle can structure as it sees fit.
    """
    # Puzzle states only work if there is a valid and authenticated visitor
    if not visitor_auth.is_active:
        return

    # Get the database model for the visitor.
    visitor = db_session.query(Visitor).filter(Visitor.uid == visitor_auth.uid).first()
    if visitor is None:
        raise VisitorUIDInvalidError(f"Could not find visitor {visitor_auth.uid} in the database.")

    # Get the database models for the puzzle.
    puzzle = get(db_session, puzzle_name)

    # Check whether a state for the puzzle and visitor already exists.
    state_model = (
        db_session.query(State)
        .filter(State.puzzle_id == puzzle.id, State.visitor_id == visitor.id)
        .first()
    )

    # If the state doesn't exist yet, create it, otherwise overwrite the state information
    if state_model is None:
        state_model = State(
            puzzle=puzzle,
            visitor=visitor,
            updated_at=datetime.now(),
            state=jsonable_encoder(json.dumps(state)),
        )
        try:
            db_session.add(state_model)
            db_session.commit()
        except Exception:
            db_session.rollback()
            raise PuzzleStateCreationError(
                f"Could not create a state for {puzzle.name} by {visitor.uid}"
            )
    else:
        state_model.updated_at = datetime.now()
        state_model.state = json.dumps(jsonable_encoder(state))

        try:
            db_session.commit()
        except Exception:
            db_session.rollback()
            raise PuzzleStateUpdatedError(
                f"Failed to update the state for  {puzzle.name} and {visitor.uid}"
            )


def generate_puzzle_qr_code(name: str, as_file_buff: bool = False) -> str | BytesIO:
    return generate_qr_code(f"{config.BASE_URL}puzzles/{name}/", as_file_buff=as_file_buff)


def generate_puzzle_qr_codes_pdf(db_session: Session):
    puzzles = get_all(db_session, only_active=False)

    module = modules["openday_scavenger"]
    module_path = module.__file__
    if module_path is not None:
        logo_path = Path(module_path).parent / "static/images/qr_codes/lock.png"
        if not logo_path.exists():
            logo_path = None
    else:
        logo_path = None

    return generate_qr_codes_pdf(
        [f"{config.BASE_URL}puzzles/{puzzle.name}/" for puzzle in puzzles],
        logo=logo_path,
        title="You Found A Puzzle Lock!",
        title_font_size=30,
        url_font_size=12,
    )


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

    start_time = datetime.now().replace(hour=9, minute=30, second=0)
    end_time = start_time + timedelta(hours=6)

    # Loop over all visitors from the pool, add them to the visitor table and
    # generate a number of responses for each puzzle.
    try:
        for visitor_from_pool in visitors_pool:
            random_time = start_time + (end_time - start_time) * random.random()
            checkout_time = random_time + (end_time - random_time) * random.random()
            visitor = Visitor(
                uid=visitor_from_pool.uid, checked_in=random_time, checked_out=checkout_time
            )
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


def upsert_puzzle_json(db_session: Session, puzzle_json: PuzzleJson):
    existing_puzzles_by_id = {item.id: item for item in get_all(db_session)}

    for puzzle in puzzle_json.puzzles:
        existing_puzzle = "id" in puzzle and existing_puzzles_by_id.get(puzzle["id"])
        if existing_puzzle:
            _ = update(db_session, existing_puzzle.name, PuzzleUpdate(**puzzle))
        else:
            _ = create(db_session, PuzzleCreate(**puzzle))
