from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from openday_scavenger.api.db import get_db
from openday_scavenger.api.puzzles.service import count as count_puzzles
from openday_scavenger.api.puzzles.service import count_responses
from openday_scavenger.api.visitors.service import count as count_visitors

router = APIRouter()

templates = Jinja2Templates(directory=Path(__file__).resolve().parent / "static")


@router.get("/")
async def render_index_page(
    request: Request,
    db: Annotated["Session", Depends(get_db)],
):
    """Render admin index page"""

    number_active_puzzles = count_puzzles(db, only_active=True)
    number_active_visitors = count_visitors(db, still_playing=True)
    number_responses = count_responses(db, only_correct=False)
    number_correct_responses = count_responses(db, only_correct=False)

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "active_page": "dashboard",
            "number_active_puzzles": number_active_puzzles,
            "number_active_visitors": number_active_visitors,
            "number_responses": number_responses,
            "number_correct_responses": number_correct_responses,
        },
    )
