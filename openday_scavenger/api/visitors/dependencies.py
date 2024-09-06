from typing import Annotated
from fastapi import Request, Depends
from sqlalchemy.orm import Session

from openday_scavenger.config import get_settings
from openday_scavenger.api.db import get_db
from openday_scavenger.api.visitors.models import Visitor
from openday_scavenger.api.visitors.schemas import VisitorAuth
from .exceptions import VisitorNotAuthenticatedError


__all__ = ["get_auth_visitor"]

config = get_settings()


async def get_auth_visitor(db_session: Annotated["Session", Depends(get_db)], request: Request) -> VisitorAuth | None:
    """ Dependency that returns an authenticated visitor """
    
    # Get the visitor uid from the cookie directly. As we make the Cookie name
    # configurable, we can't use the Cookie dependency injection but get it from
    # the request object.
    visitor_uid = request.cookies.get(config.COOKIE_KEY)
    
    # If the cookie doesn't exist, this means the visitor is not authenticated
    if visitor_uid is None:
        return None

    # Look up the visitor in the database. We don't use a separate session management
    # here, but use the visitor identity table directly. This is not something you
    # would do in a proper system, but for our purpose this is acceptable.
    visitor = db_session.query(Visitor).filter(Visitor.uid == visitor_uid).first()
    if visitor is None:
        return None

    # Cast the database model to a pydantic schema, so we maintain a little bit
    # of abstraction.
    result = VisitorAuth(uid=visitor.uid)
    return result


async def auth_required(visitor: Annotated[VisitorAuth | None, Depends(get_auth_visitor)]):
    """ Raises an exception if the visitor is not authenticated """
    if visitor is None:
        raise VisitorNotAuthenticatedError("Visitor is not authenticated")
