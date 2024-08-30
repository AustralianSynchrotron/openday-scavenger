from typing import Annotated
from pathlib import Path
from datetime import datetime
from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from openday_scavenger.api.db import get_db

from openday_scavenger.api.visitors.service import get_all, create, check_out
from openday_scavenger.api.visitors.schemas import VisitorCreate

router = APIRouter()

templates = Jinja2Templates(directory=Path(__file__).resolve().parent / "static")


@router.get("/")
async def render_visitor_page(request: Request):
    """ Render the puzzle admin page """
    return templates.TemplateResponse(
        request=request,
        name="visitors.html"
    )


@router.post("/")
async def create_visitor(visitor_in: VisitorCreate, request: Request, db: Annotated["Session", Depends(get_db)]):
    """Create a new visitor"""
    _ = create(db, visitor_in)
    return await _render_visitor_table(request, db)


@router.post("/{visitor_uid}/checkout")
async def update_visitor(visitor_uid: str, request: Request, db: Annotated["Session", Depends(get_db)]):
    """ Update a single puzzle and re-render the table """
    _ = check_out(db, visitor_uid)
    return await _render_visitor_table(request, db)

@router.get("/table")
async def render_visitor_table(request: Request, db: Annotated["Session", Depends(get_db)]):
    """ Render the table of visitors on the admin page """
    return await _render_visitor_table(request, db)


async def _render_visitor_table(request: Request, db: Annotated["Session", Depends(get_db)]):
    visitors = get_all(db)

    return templates.TemplateResponse(
        request=request,
        name="visitors_table.html",
        context={"visitors": visitors, "now": datetime.now()}
    )