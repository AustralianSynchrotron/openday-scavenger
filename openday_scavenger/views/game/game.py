from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from openday_scavenger.api.db import get_db
from openday_scavenger.api.puzzles.schemas import PuzzleCompare
from openday_scavenger.api.puzzles.service import compare_answer
from openday_scavenger.api.visitors.dependencies import get_auth_visitor
from openday_scavenger.api.visitors.exceptions import VisitorExistsError
from openday_scavenger.api.visitors.schemas import VisitorAuth
from openday_scavenger.api.visitors.service import create as create_visitor
from openday_scavenger.config import get_settings

router = APIRouter()
config = get_settings()
templates = Jinja2Templates(directory=Path(__file__).resolve().parent / "static")


@router.get("/")
async def render_root_page(
    request: Request, visitor: Annotated[VisitorAuth | None, Depends(get_auth_visitor)]
):
    """Render the starting page for visitors"""
    return templates.TemplateResponse(
        request=request, name="index.html", context={"visitor": visitor}
    )


@router.get("/register/{visitor_uid}")
async def register_visitor(visitor_uid: str, db: Annotated["Session", Depends(get_db)]):
    """Register a new visitor and set the authentication cookie"""

    # Registration of a visitor means we check if the uid is available in the visitor pool, and if so
    # we pop that uid out of the pool and store a new visitor entry with the supplied
    # uid in the database and "authenticate" the user by setting a cookie.
    # If the visitor already exists, we set the Cookie regardless. This allows visitors to
    # get their session back easily if something happened to their phone. This is not something
    # that you would do in a proper application ever! Since our visitors are anonymous
    # and are not told what their uid is, the worst case is that a visitor finds the
    # uid of another visitor and hijacks their session. If they figure that out, props
    # to them for successfully hacking our little application. We might want to hire them.
    try:
        _ = create_visitor(db, visitor_uid)
    except VisitorExistsError:
        pass

    # Authenticate the visitor.
    # Since the visitor uid is random and anonymous, we store it in a cookie and use this to flag that a visitor is logged in.
    # Usually you would not use the uid of a user's identity as their session identifier and have a separate session management
    # system, but for our purposes this is good enough.
    response = RedirectResponse("/")
    response.set_cookie(
        key=config.COOKIE_KEY,
        value=visitor_uid,
        max_age=config.COOKIE_MAX_AGE,
        domain=config.BASE_URL.host,
        secure=config.BASE_URL.scheme == "https",
        httponly=True,
        samesite="strict",
    )
    return response


@router.post("/submission")
async def submit_answer(
    puzzle_in: Annotated[PuzzleCompare, Form()], db: Annotated["Session", Depends(get_db)]
):
    """AJAX style endpoint to submit the answer to a puzzle"""

    if compare_answer(db, puzzle_in):
        return {"success": True}
    else:
        return {"success": False}
