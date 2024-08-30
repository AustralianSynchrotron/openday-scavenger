from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from openday_scavenger.api.db import get_db
from openday_scavenger.api.puzzles.schemas import PuzzleCreate, PuzzleUpdate
from openday_scavenger.api.puzzles.service import (
    create,
    generate_qr_code,
    get_all,
    update,
)

router = APIRouter()

templates = Jinja2Templates(directory=Path(__file__).resolve().parent / "static")


@router.get("/")
async def render_puzzle_page(request: Request):
    """Render the puzzle admin page"""
    return templates.TemplateResponse(request=request, name="puzzles.html")


@router.post("/")
async def create_puzzle(
    puzzle: PuzzleCreate, request: Request, db: Annotated["Session", Depends(get_db)]
):
    """Create a new puzzle and re-render the table"""
    puzzle = create(db, puzzle)
    return await _render_puzzles_table(request, db)


@router.get("/table")
async def render_puzzle_table(
    request: Request, db: Annotated["Session", Depends(get_db)]
):
    """Render the table of puzzles on the admin page"""
    return await _render_puzzles_table(request, db)


@router.put("/{puzzle_id}")
async def update_puzzle(
    puzzle: PuzzleUpdate, request: Request, db: Annotated["Session", Depends(get_db)]
):
    """Update a single puzzle and re-render the table"""
    puzzle = update(db, puzzle)
    return await _render_puzzles_table(request, db)


@router.get("/qr/{name}")
async def render_qr_code(name: str, request: Request):
    qr = generate_qr_code(name)

    return templates.TemplateResponse(
        request=request, name="qr.html", context={"qr": qr}
    )


async def _render_puzzles_table(
    request: Request, db: Annotated["Session", Depends(get_db)]
):
    puzzles = get_all(db)

    return templates.TemplateResponse(
        request=request, name="puzzles_table.html", context={"puzzles": puzzles}
    )
    return templates.TemplateResponse(
        request=request, name="puzzles_table.html", context={"puzzles": puzzles}
    )
