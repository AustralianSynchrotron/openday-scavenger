from typing import Annotated
from pathlib import Path
from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from openday_scavenger.api.db import get_db
from openday_scavenger.api.puzzles.service import get_all, create, update
from openday_scavenger.api.puzzles.schemas import PuzzleCreate, PuzzleUpdate


router = APIRouter()

templates = Jinja2Templates(directory=Path(__file__).resolve().parent / "static")


@router.get("/")
async def render_puzzle_page(request: Request):
    """ Render the puzzle admin page """
    return templates.TemplateResponse(
        request=request,
        name="puzzles.html"
    )


@router.post("/")
async def create_puzzle(puzzle: PuzzleCreate, request: Request, db: Annotated["Session", Depends(get_db)]):
    """ Create a new puzzle and re-render the table """
    puzzle = create(db, puzzle)
    return await _render_puzzles_table(request, db)


@router.get("/table")
async def render_puzzle_table(request: Request, db: Annotated["Session", Depends(get_db)]):
    """ Render the table of puzzles on the admin page """
    return await _render_puzzles_table(request, db)


@router.put("/{puzzle_id}")
async def update_puzzle(puzzle: PuzzleUpdate, request: Request, db: Annotated["Session", Depends(get_db)]):
    """ Update a single puzzle and re-render the table """
    puzzle = update(db, puzzle)
    return await _render_puzzles_table(request, db)


async def _render_puzzles_table(request: Request, db: Annotated["Session", Depends(get_db)]):
    puzzles = get_all(db)

    return templates.TemplateResponse(
        request=request,
        name="puzzles_table.html",
        context={"puzzles": puzzles}
    )
