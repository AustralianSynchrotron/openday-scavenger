import json
from datetime import datetime
from io import BytesIO
from typing import Any
from uuid import uuid4

from sqlalchemy import Integer, Row, and_, cast, func
from sqlalchemy.orm import Query, Session

from openday_scavenger.api.puzzles.models import Puzzle, Response
from openday_scavenger.api.qr_codes import generate_qr_code, generate_qr_codes_pdf
from openday_scavenger.config import get_settings

from .exceptions import VisitorExistsError, VisitorUIDInvalidError
from .models import Visitor, VisitorPool
from .schemas import VisitorPoolCreate

config = get_settings()


def get_all(
    db_session: Session,
    uid_filter: str | None = None,
    still_playing: bool | None = None,
) -> list[Row[tuple[Visitor, int, int]]]:
    """
    Retrieves all visitors with their correct answer count from the database, applying filters if provided.

    Args:
        db_session (Session): The SQLAlchemy session object.
        uid_filter (str, optional): A string to filter visitors by their UID (prefix match).
        still_playing (bool, optional): Whether to filter for visitors who are still playing (checked_out is None).

    Returns:
        List[tuple[Visitor, int]]
    """
    q = _filter(db_session.query(Visitor), uid_filter=uid_filter, still_playing=still_playing)

    q = (
        q.outerjoin(Response, Visitor.id == Response.visitor_id)
        .group_by(Visitor.id)
        .with_entities(
            Visitor,
            func.sum(cast(Response.is_correct, Integer)).label("correct_answers"),
            func.count(func.distinct(Response.puzzle_id)).label("attempted_puzzles"),
        )
    )

    return q.all()  # type: ignore


def create(
    db_session: Session, *, visitor_uid: str, extra: dict[str, Any] | None = None
) -> Visitor:
    """
    Create a new visitor entry in the database.

    Args:
        db_session (Session): The SQLAlchemy session object.
        visitor_uid (str): The uid of the visitor that should be added to the database.
        extra (dict): Extra information about the user that is stored as a JSON string.

    Returns:
        Visitor: The created visitor database model.
    """

    # Check first whether the visitor already exists
    visitor = db_session.query(Visitor).filter(Visitor.uid == visitor_uid).first()
    if visitor is not None:
        raise VisitorExistsError(f"Visitor {visitor.uid} already exists")

    # Check if the UID is available in the visitor pool
    visitor_pool = db_session.query(VisitorPool).filter(VisitorPool.uid == visitor_uid).first()
    if visitor_pool is None:
        raise VisitorUIDInvalidError(f"UID {visitor_uid} not in visitor pool")

    # Create the visitor database model and add it to the database
    visitor = Visitor(
        uid=visitor_uid,
        checked_in=datetime.now(),
        extra=json.dumps(extra) if extra is not None else None,
    )

    try:
        db_session.add(visitor)
        db_session.delete(visitor_pool)
        db_session.commit()
    except:
        db_session.rollback()
        raise

    return visitor


def check_out(db_session: Session, *, visitor_uid: str) -> Visitor:
    """
    Check out a visitor, which ends their session and they can't play any longer.

    Args:
        db_session (Session): The SQLAlchemy session object.
        visitor_uid (str): The uid of the visitor that should be checked out.

    Returns:
        Visitor: The visitor database model.

    """
    visitor = db_session.query(Visitor).filter(Visitor.uid == visitor_uid).first()

    if visitor is None:
        raise VisitorUIDInvalidError(f"The uid {visitor_uid} is not valid")

    try:
        visitor.checked_out = datetime.now()
        db_session.commit()
    except:
        db_session.rollback()
        raise

    return visitor


def get_correct_responses(db_session: Session, *, visitor_uid: str) -> list[Response]:
    """
    Get the correct responses for the visitor.

    Args:
        db_session (Session): The SQLAlchemy session object.
        visitor_uid (str): The uid of the visitor for whom the correct
                           responses should be returned.

    Returns:
        list[Response]: The correct responses for the visitor.
    """
    visitor = db_session.query(Visitor).filter(Visitor.uid == visitor_uid).first()

    if visitor is None:
        raise VisitorUIDInvalidError(f"The uid {visitor_uid} is not valid")

    return visitor.correct_responses


def has_completed_all_puzzles(db_session: Session, *, visitor_uid: str) -> bool:
    """
    Check whether a visitor has completed all their puzzles.

    Args:
        db_session (Session): The SQLAlchemy session object.
        visitor_uid (str): The uid of the visitor that should be checked.

    Returns:
        bool: True of the visitor has completed all their puzzles.
    """
    number_active_puzzles = db_session.query(Puzzle).filter(Puzzle.active).count()
    correct_responses = get_correct_responses(db_session=db_session, visitor_uid=visitor_uid)
    return len(correct_responses) >= number_active_puzzles


def get_visitor_pool(db_session: Session, *, limit: int = 10) -> list[VisitorPool]:
    """
    Return the visitors in the visitor pool.

    Args:
        db_session (Session): The SQLAlchemy session object.
        limit (int): Limit the returned visitors from the pool to this number.

    Returns:
        list[VisitorPool]: List of visitors from the pool.
    """
    return db_session.query(VisitorPool).limit(limit).all()


def create_visitor_pool(db_session: Session, pool_in: VisitorPoolCreate) -> None:
    """
    Add the specified number of new visitors with random uids to the visitor pool.

    Args:
        db_session (Session): The SQLAlchemy session object.
        pool_in (VisitorPoolCreate): The object containing the settings for the creation.
    """
    existing_uuids = {id for (id,) in db_session.query(VisitorPool.uid)}
    uuids = set([str(uuid4())[:6] for _ in range(pool_in.number_of_entries)])

    # Remove duplicates.
    uuids = uuids - existing_uuids

    try:
        db_session.add_all([VisitorPool(uid=uuid) for uuid in uuids])
        db_session.commit()
    except Exception:
        db_session.rollback()
        raise


def generate_visitor_qr_code(uid: str, as_file_buff: bool = False) -> str | BytesIO:
    return generate_qr_code(f"{config.BASE_URL}register/{uid}", as_file_buff=as_file_buff)


def generate_visitor_qr_codes_pdf(db_session: Session):
    visitors = get_visitor_pool(db_session)

    return generate_qr_codes_pdf(
        [f"{config.BASE_URL}register/{visitor.uid}" for visitor in visitors]
    )


def _filter(
    query: Query, *, uid_filter: str | None = None, still_playing: bool | None = None
) -> Query:
    """
    Applies filters to the provided SQLAlchemy query.

    Args:
        query (Query): The base query to apply filters to.
        uid_filter (str, optional): A string to filter visitors by their UID (prefix match).
        still_playing (bool, optional): Whether to filter for visitors who are still playing (checked_out is None).

    Returns:
        Query: The filtered query object.
    """

    filters = []
    if uid_filter is not None:
        filters.append(Visitor.uid.like(f"{uid_filter}%"))

    if still_playing:
        filters.append(
            Visitor.checked_out.is_(None)
        )  # Use .is_(None) for NULL comparison  # Filter for visitors who are still playing

    if filters:
        query = query.filter(and_(*filters))

    return query
