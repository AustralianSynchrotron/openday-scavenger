from datetime import datetime
from uuid import uuid4

from sqlalchemy import Integer, Row, and_, cast, func
from sqlalchemy.orm import Query, Session

from openday_scavenger.api.puzzles.models import Response

from .exceptions import VisitorExistsError, VisitorUIDInvalidError
from .models import Visitor, VisitorPool
from .schemas import VisitorPoolCreate


def _filter(
    query: Query, uid_filter: str | None = None, still_playing: bool | None = None
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


def get_all(
    db_session: Session,
    uid_filter: str | None = None,
    still_playing: bool | None = None,
    with_stats: bool | None = False,
) -> list[Visitor | Row[tuple[Visitor, int, int]]]:
    """
    Retrieves all visitors with their correct answer count from the database, applying filters if provided.

    Args:
        db_session (Session): The SQLAlchemy session object.
        uid_filter (str, optional): A string to filter visitors by their UID (prefix match).
        still_playing (bool, optional): Whether to filter for visitors who are still playing (checked_out is None).
        with_stats (bool, optional): Whether to provide playing statistics in response.
    Returns:
        List[Union[Visitor, tuple[Visitor, int]]]:
            - If with_stats is False: a list of Visitor objects
            - If with_stats is True: a list of tuples containing Visitor data and correct answer count.
    """

    q = _filter(db_session.query(Visitor), uid_filter, still_playing)

    if with_stats:
        q = (
            q.outerjoin(Response, Visitor.id == Response.visitor_id)
            .group_by(Visitor.uid)
            .with_entities(
                Visitor,
                func.sum(cast(Response.is_correct, Integer)).label("correct_answers"),
                func.count(func.distinct(Response.puzzle_id)).label("attempted_puzzles"),
            )
        )
        q = q.group_by(Visitor.uid)

    return q.all()  # type: ignore


def create(db_session: Session, visitor_uid: str) -> Visitor:
    """Create a new visitor"""

    # Check first whether the visitor already exists
    visitor = db_session.query(Visitor).filter(Visitor.uid == visitor_uid).first()
    if visitor is not None:
        raise VisitorExistsError(f"Visitor {visitor.uid} already exists")

    # Check if the UID is available in the visitor pool
    visitor_pool = db_session.query(VisitorPool).filter(VisitorPool.uid == visitor_uid).first()
    if visitor_pool is None:
        raise VisitorUIDInvalidError(f"UID {visitor_uid} not in visitor pool")

    # Create the visitor database model and add it to the database
    visitor = Visitor(uid=visitor_uid, checked_in=datetime.now())

    try:
        db_session.add(visitor)
        db_session.delete(visitor_pool)
        db_session.commit()
    except:
        db_session.rollback()
        raise

    return visitor


def check_out(db_session: Session, visitor_uid: str):
    visitor = db_session.query(Visitor).filter(Visitor.uid == visitor_uid).first()
    visitor.checked_out = datetime.now()

    try:
        db_session.commit()
    except:
        db_session.rollback()
        raise

    return visitor


def create_visitor_pool(db_session: Session, pool_in: VisitorPoolCreate):
    existing_uuids = {id for (id,) in db_session.query(VisitorPool.uid)}
    uuids = set([str(uuid4())[:6] for i in range(pool_in.number_of_entries)])
    # Remove duplicates.
    uuids = uuids - existing_uuids

    try:
        db_session.add_all([VisitorPool(uid=uuid) for uuid in uuids])
        db_session.commit()
    except Exception:
        db_session.rollback()
        raise


def get_visitor_pool(db_session: Session, number_of_entries: int = 10):
    existing_uuids = {id for (id,) in db_session.query(VisitorPool.uid).limit(number_of_entries)}
    return existing_uuids
