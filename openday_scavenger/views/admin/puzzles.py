from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from openday_scavenger.api.db import get_db
from openday_scavenger.api.puzzles.schemas import PuzzleCreate, PuzzleUpdate
from openday_scavenger.api.puzzles.service import (
    create,
    generate_puzzle_qr_code,
    generate_puzzle_qr_codes_pdf,
    get_all,
    update,
)
from openday_scavenger.config import get_settings

router = APIRouter()
config = get_settings()
templates = Jinja2Templates(directory=Path(__file__).resolve().parent / "static")


@router.get("/")
async def render_puzzle_page(request: Request):
    """Render the puzzle admin page"""
    return templates.TemplateResponse(request=request, name="puzzles.html")


@router.post("/")
async def create_puzzle(
    puzzle_in: PuzzleCreate, request: Request, db: Annotated["Session", Depends(get_db)]
):
    """Create a new puzzle and re-render the table"""
    _ = create(db, puzzle_in)
    return await _render_puzzles_table(request, db)


@router.get("/table")
async def render_puzzle_table(request: Request, db: Annotated["Session", Depends(get_db)]):
    """Render the table of puzzles on the admin page"""
    return await _render_puzzles_table(request, db)


@router.put("/{puzzle_name}")
async def update_puzzle(
    puzzle_name: str,
    puzzle_in: PuzzleUpdate,
    request: Request,
    db: Annotated["Session", Depends(get_db)],
):
    """Update a single puzzle and re-render the table"""
    _ = update(db, puzzle_name, puzzle_in)
    return await _render_puzzles_table(request, db)


@router.get("/{puzzle_name}/qr")
async def render_qr_code(puzzle_name: str, request: Request):
    qr = generate_puzzle_qr_code(puzzle_name)

    return templates.TemplateResponse(request=request, name="qr.html", context={"qr": qr})


@router.get("/download-pdf")
async def download_qr_codes(db: Annotated["Session", Depends(get_db)]):
    pdf_io = generate_puzzle_qr_codes_pdf(db)

    return StreamingResponse(
        pdf_io,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=puzzle_qr_codes.pdf"},
    )


async def _render_puzzles_table(request: Request, db: Annotated["Session", Depends(get_db)]):
    puzzles = get_all(db)

    return templates.TemplateResponse(
        request=request,
        name="puzzles_table.html",
        context={"puzzles": puzzles, "base_url": config.BASE_URL},
    )
