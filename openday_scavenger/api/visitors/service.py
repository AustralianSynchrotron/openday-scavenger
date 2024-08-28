from datetime import datetime
from sqlalchemy.orm import Session
from openday_scavenger.api.visitors.models import Visitor
from openday_scavenger.api.visitors.schemas import VisitorCreate, VisitorUpdate


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

def update(db_session: Session, visitor_in: VisitorUpdate):
    update_data = visitor_in.model_dump(exclude_unset=True)

    visitor = db_session.query(Visitor).filter(Visitor.id == update_data["id"]).first()    

    # map the pydantic model to database model explicitly to maintain abstraction
    visitor.uid = update_data.get("uid", visitor.uid)
    visitor.checked_in = update_data.get("checked_in", visitor.checked_in)
    if update_data.get("check_out"):
        visitor.checked_out = datetime.now()
    visitor.checked_out = update_data.get("checked_out", visitor.checked_out)
    
    try:
        db_session.commit()
    except:
        db_session.rollback()
        raise

    return visitor