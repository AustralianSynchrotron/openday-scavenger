from datetime import datetime
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from openday_scavenger.api.db import get_db
from openday_scavenger.api.puzzles.service import get_all as get_all_puzzles
from openday_scavenger.api.visitors.schemas import VisitorCreate, VisitorPoolCreate
from openday_scavenger.api.visitors.service import (
    check_out,
    create,
    create_visitor_pool,
    generate_visitor_qr_code,
    generate_visitor_qr_codes_pdf,
    get_visitor_pool,
)
from openday_scavenger.api.visitors.service import get_all as get_all_visitors
from openday_scavenger.config import get_settings

router = APIRouter()
config = get_settings()
templates = Jinja2Templates(directory=Path(__file__).resolve().parent / "static")


@router.get("/")
async def render_visitor_page(request: Request):
    """Render the puzzle admin page"""
    return templates.TemplateResponse(request=request, name="visitors.html")


@router.post("/")
async def create_visitor(
    visitor_in: VisitorCreate, request: Request, db: Annotated["Session", Depends(get_db)]
):
    """Create a new visitor"""
    _ = create(db, visitor_uid=visitor_in.uid)
    return await _render_visitor_table(request, db)


@router.post("/{visitor_uid}/checkout")
async def update_visitor(
    visitor_uid: str, request: Request, db: Annotated["Session", Depends(get_db)]
):
    """Update a single puzzle and re-render the table"""
    _ = check_out(db, visitor_uid=visitor_uid)
    return await _render_visitor_table(request, db)


@router.get("/table")
async def render_visitor_table(
    request: Request,
    db: Annotated["Session", Depends(get_db)],
    uid_filter: str | None = None,
    still_playing: bool | None = None,
):
    """Render the table of visitors on the admin page"""
    return await _render_visitor_table(request, db, uid_filter, still_playing)


@router.post("/pool")
async def initialise_visitor_pool(
    request: Request,
    db: Annotated["Session", Depends(get_db)],
    pool_in: VisitorPoolCreate = VisitorPoolCreate(),
):
    create_visitor_pool(db, pool_in=pool_in)
    return await _render_visitor_pool_table(request, db)


@router.get("/{visitor_uid}/qr")
async def render_qr_code(visitor_uid: str, request: Request):
    qr = generate_visitor_qr_code(visitor_uid)

    return templates.TemplateResponse(request=request, name="qr.html", context={"qr": qr})


@router.get("/pool")
async def render_visitor_pool_table(
    request: Request, db: Annotated["Session", Depends(get_db)], limit: int = 10
):
    """Render the table of possible visitor uids on the admin page"""
    return await _render_visitor_pool_table(request, db, limit)


@router.get("/download-pdf")
async def download_qr_codes(db: Annotated["Session", Depends(get_db)]):
    pdf_io = generate_visitor_qr_codes_pdf(db)

    return StreamingResponse(
        pdf_io,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=visitor_qr_codes.pdf"},
    )


async def _render_visitor_table(
    request: Request,
    db: Annotated["Session", Depends(get_db)],
    uid_filter: str | None = None,
    still_playing: bool | None = None,
):
    visitors = get_all_visitors(db, uid_filter=uid_filter, still_playing=still_playing)
    number_enabled_puzzles = len(get_all_puzzles(db, only_active=True))

    return templates.TemplateResponse(
        request=request,
        name="visitors_table.html",
        context={
            "visitors": visitors,
            "number_enabled_puzzles": number_enabled_puzzles,
            "now": datetime.now(),
        },
    )


async def _render_visitor_pool_table(
    request: Request, db: Annotated["Session", Depends(get_db)], limit: int = 10
):
    visitor_pool = get_visitor_pool(db, limit=limit)

    return templates.TemplateResponse(
        request=request,
        name="visitor_pool_table.html",
        context={"visitor_pool": visitor_pool, "base_url": config.BASE_URL},
    )
