from datetime import datetime
from sqlalchemy.orm import Session
from openday_scavenger.api.visitors.models import Visitor
from openday_scavenger.api.visitors.schemas import VisitorCreate


def get_all(db_session: Session) -> list[Visitor]:
    return db_session.query(Visitor).all()


def create(db_session: Session, visitor_in: VisitorCreate):

    visitor = Visitor(
        uid = visitor_in.uid,
        checked_in = datetime.now()
    )
    db_session.add(visitor)

    try:
        db_session.commit()
    except:
        db_session.rollback()
        raise

    return visitor