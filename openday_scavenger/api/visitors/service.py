from datetime import datetime
from uuid import uuid4

from sqlalchemy.orm import Session

from .exceptions import VisitorExistsError, VisitorUIDInvalidError
from .models import Visitor, VisitorPool
from .schemas import VisitorPoolCreate


def get_all(
    db_session: Session, uid_filter: str | None = None, still_playing: bool | None = None
) -> list[Visitor]:
    q = db_session.query(Visitor)
    if uid_filter is not None:
        q = q.filter(Visitor.uid.like(f"{uid_filter}%"))
    if still_playing is not None:
        q = q.filter(Visitor.checked_out == None)  # noqa E711
    return q.all()


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
