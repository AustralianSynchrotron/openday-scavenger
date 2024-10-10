from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, Form, Header, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from openday_scavenger.api.db import get_db
from openday_scavenger.api.puzzles.schemas import PuzzleCompare
from openday_scavenger.api.puzzles.service import compare_answer, get_all_responses
from openday_scavenger.api.puzzles.service import count as count_puzzles
from openday_scavenger.api.visitors.dependencies import get_auth_visitor
from openday_scavenger.api.visitors.exceptions import VisitorExistsError
from openday_scavenger.api.visitors.schemas import VisitorAuth
from openday_scavenger.api.visitors.service import create as create_visitor
from openday_scavenger.api.visitors.service import get_correct_responses
from openday_scavenger.api.visitors.service import (
    has_completed_all_puzzles as visitor_has_completed_all_puzzles,
)
from openday_scavenger.config import get_settings

router = APIRouter()
config = get_settings()
templates = Jinja2Templates(directory=Path(__file__).resolve().parent / "static")


@router.get("/")
async def render_root_page(
    request: Request,
    visitor: Annotated[VisitorAuth, Depends(get_auth_visitor)],
    db: Annotated["Session", Depends(get_db)],
):
    """Render the starting page for visitors"""

    # If the visitor has completed all puzzles, don't show the QR code scanner
    # and send them back to the registration desk. Also get the progress of the visitor.
    has_completed_all_puzzles = False
    number_correct_responses = 0
    if (config.SESSIONS_ENABLED) and (visitor.uid is not None):
        has_completed_all_puzzles = visitor_has_completed_all_puzzles(db, visitor_uid=visitor.uid)
        number_correct_responses = len(get_correct_responses(db, visitor_uid=visitor.uid))

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "visitor": visitor,
            "number_active_puzzles": count_puzzles(db, only_active=True),
            "number_correct_responses": number_correct_responses,
            "has_completed_all_puzzles": has_completed_all_puzzles,
        },
    )


@router.get("/register/{visitor_uid}")
async def register_visitor(
    visitor_uid: str,
    db: Annotated["Session", Depends(get_db)],
    user_agent: Annotated[str | None, Header()] = None,
):
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
        _ = create_visitor(db, visitor_uid=visitor_uid, extra={"user_agent": user_agent})
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
        samesite="none" if config.BASE_URL.scheme == "https" else "lax",
    )
    return response


@router.post("/submission")
async def submit_answer(
    request: Request,
    puzzle_in: Annotated[PuzzleCompare, Form()],
    db: Annotated["Session", Depends(get_db)],
    visitor: Annotated[VisitorAuth, Depends(get_auth_visitor)],
):
    """
    Endpoint for submitting the puzzle answer.

    This endpoint will check whether the visitor's answer was
    correct and return the appropriate HTML page:
    - if the answer was correct and the visitor has completed
      all the puzzles, we congratulate the visitor and send them
      back to the registration desk so they can pick up their prize.
    - if the answer was correct and the visitor has not completed
      all the puzzles, we congratulate the visitor for solving the
      puzzle and provide them with a button which sends them back
      to the main starting page with the QR scanner.
    - if the answer was not correct, we say sorry and provide a button
      which will take them back to the puzzle page so they can try again.
    """
    # Check if visitor has already given a correct answer for this puzzle
    responses = get_all_responses(
        db, filter_by_puzzle_name=puzzle_in.name, filter_by_visitor_uid=visitor.uid
    )

    if any([response.is_correct for response in responses]):
        return templates.TemplateResponse(request=request, name="puzzle_correct.html")

    # Compare the answer and render the appropriate page
    if compare_answer(
        db, puzzle_name=puzzle_in.name, visitor_auth=visitor, answer=puzzle_in.answer
    ):
        if (
            (visitor.is_active)
            and (visitor.uid is not None)
            and (visitor_has_completed_all_puzzles(db, visitor_uid=visitor.uid))
        ):
            return templates.TemplateResponse(request=request, name="puzzle_completed.html")
        else:
            return templates.TemplateResponse(request=request, name="puzzle_correct.html")
    else:
        return templates.TemplateResponse(
            request=request, name="puzzle_incorrect.html", context={"puzzle": puzzle_in.name}
        )
