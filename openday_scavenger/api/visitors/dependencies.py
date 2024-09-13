from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.orm import Session

from openday_scavenger.api.db import get_db
from openday_scavenger.api.visitors.models import Visitor
from openday_scavenger.api.visitors.schemas import VisitorAuth
from openday_scavenger.config import get_settings

from .exceptions import VisitorNotAuthenticatedError

__all__ = ("get_auth_visitor", "auth_required")

config = get_settings()


async def get_auth_visitor(
    db_session: Annotated["Session", Depends(get_db)], request: Request
) -> VisitorAuth:
    """
    Dependency that returns a visitor object with auth information.

    Args:
        db_session (Session): The SQLAlchemy session object.
        request (Request): The FastAPI Request object.

    Returns:
        VisitorAuth: Visitor object with information whether the visitor
                     has been successfully authenticated or not.
    """
    # If the session management is enabled, return a VisitorAuth object with.
    # If the session management is disabled, return a VisitorAuth object with
    # the visitor uid set to None, and authentication set to True.
    if not config.SESSIONS_ENABLED:
        return VisitorAuth(uid=None, is_authenticated=True)

    # Get the visitor uid from the cookie directly. As we make the Cookie name
    # configurable, we can't use the Cookie dependency injection but get it from
    # the request object.
    visitor_uid = request.cookies.get(config.COOKIE_KEY)

    # If the cookie doesn't exist, this means the visitor is not authenticated
    if visitor_uid is None:
        return VisitorAuth(uid=None, is_authenticated=False)

    # Look up the visitor in the database. We don't use a separate session management
    # here, but use the visitor identity table directly. This is not something you
    # would do in a proper system, but for our purpose this is acceptable.
    visitor = db_session.query(Visitor).filter(Visitor.uid == visitor_uid).first()
    if visitor is None:
        return VisitorAuth(uid=None, is_authenticated=False)

    # If the visitor has been checked out, they can't play any longer.
    if visitor.is_checked_out:
        return VisitorAuth(uid=visitor.uid, is_authenticated=False)

    # The visitor is properly authenticated
    return VisitorAuth(uid=visitor.uid, is_authenticated=True)


async def auth_required(visitor: Annotated[VisitorAuth, Depends(get_auth_visitor)]):
    """
    Raises an exception if the visitor is not authenticated

    Args:
        visitor (VisitorAuth): The visitor object containing auth information.
    """
    if (config.SESSIONS_ENABLED) and (not visitor.is_authenticated):
        raise VisitorNotAuthenticatedError("Visitor is not authenticated")
