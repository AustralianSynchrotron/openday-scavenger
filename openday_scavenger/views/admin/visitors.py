from sqlite3 import dbapi2
from typing import Annotated
from pathlib import Path
from datetime import datetime
from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from openday_scavenger.api.db import get_db
from openday_scavenger.config import get_settings
from openday_scavenger.api.visitors.schemas import VisitorCreate, VisitorPoolCreate
from openday_scavenger.api.visitors.service import get_all, create, check_out, create_visitor_pool, get_visitor_pool

router = APIRouter()
config = get_settings()
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
    _ = create(db, visitor_in.uid)
    return await _render_visitor_table(request, db)


@router.post("/{visitor_uid}/checkout")
async def update_visitor(visitor_uid: str, request: Request, db: Annotated["Session", Depends(get_db)]):
    """ Update a single puzzle and re-render the table """
    _ = check_out(db, visitor_uid)
    return await _render_visitor_table(request, db)

@router.get("/table")
async def render_visitor_table(request: Request, db: Annotated["Session", Depends(get_db)], uid_filter: str | None = None):
    """ Render the table of visitors on the admin page """
    return await _render_visitor_table(request, db, uid_filter)

@router.post("/pool")
async def initialise_visitor_pool(request: Request, db: Annotated["Session", Depends(get_db)], pool_in: VisitorPoolCreate | None = VisitorPoolCreate()):
    create_visitor_pool(db, pool_in=pool_in)
    return await _render_visitor_pool_table(request, db)

@router.get("/pool")
async def render_visitor_pool_table(request: Request, db: Annotated["Session", Depends(get_db)], number_of_entries: int = 10):
    """ Render the table of possible visitor uids on the admin page """
    return await _render_visitor_pool_table(request, db, number_of_entries)


async def _render_visitor_table(request: Request, db: Annotated["Session", Depends(get_db)], uid_filter: str | None = None):
    visitors = get_all(db, uid_filter=uid_filter)

    return templates.TemplateResponse(
        request=request,
        name="visitors_table.html",
        context={"visitors": visitors, "now": datetime.now()}
    )

async def _render_visitor_pool_table(request: Request, db: Annotated["Session", Depends(get_db)], number_of_entries: int = 10):
    visitor_pool = get_visitor_pool(db, number_of_entries=number_of_entries)

    return templates.TemplateResponse(
        request=request,
        name="visitor_pool_table.html",
        context={"visitor_pool_uids": visitor_pool, "base_url": config.BASE_URL}
    ) 