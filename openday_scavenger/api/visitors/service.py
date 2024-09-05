from datetime import datetime
from sqlalchemy.orm import Session
from openday_scavenger.api.visitors.models import Visitor


def get_all(db_session: Session, uid_filter: str | None = None) -> list[Visitor]:
    q = db_session.query(Visitor)
    if uid_filter is not None:
        q = q.filter(Visitor.uid.like(f"{uid_filter}%"))
    return q.all()


def create(db_session: Session, visitor_uid: str):

    visitor = Visitor(
        uid = visitor_uid,
        checked_in = datetime.now()
    )
    db_session.add(visitor)

    try:
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
