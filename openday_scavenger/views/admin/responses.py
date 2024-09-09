from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from openday_scavenger.api.db import get_db
from openday_scavenger.api.puzzles.service import get_all_responses

router = APIRouter()

templates = Jinja2Templates(directory=Path(__file__).resolve().parent / "static")


@router.get("/")
async def render_response_page(request: Request):
    """Render the responses admin page"""
    return templates.TemplateResponse(request=request, name="responses.html")


@router.get("/table")
async def render_response_table(
    request: Request,
    db: Annotated["Session", Depends(get_db)],
    puzzle_name: str | None = None,
    visitor_uid: str | None = None,
):
    """Render the table of responses on the admin page"""

    # We ask the service layer to give us all the responses, optionally filtered by
    # the first letters of the the puzzle name or visitor uid.
    responses = get_all_responses(
        db, filter_by_puzzle_name=puzzle_name, filter_by_visitor_uid=visitor_uid
    )

    return templates.TemplateResponse(
        request=request, name="responses_table.html", context={"responses": responses}
    )
