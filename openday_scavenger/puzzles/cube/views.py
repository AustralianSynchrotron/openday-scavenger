from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from openday_scavenger.api.db import get_db
from openday_scavenger.api.puzzles.service import get_puzzle_state, set_puzzle_state
from openday_scavenger.api.visitors.dependencies import get_auth_visitor
from openday_scavenger.api.visitors.schemas import VisitorAuth

PUZZLE_NAME = "cube"
router = APIRouter()
templates = Jinja2Templates(directory=Path(__file__).resolve().parent / "static")


@router.get("/static/{path:path}")
async def get_static_files(path: Path):
    """Serve files from a local static folder"""
    parent_path = Path(__file__).resolve().parent / "static"
    file_path = parent_path / path
    if file_path.is_relative_to(parent_path) and file_path.is_file():
        return FileResponse(file_path)
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Requested file does not exist"
        )


@router.get("/")
@router.get("")
async def index(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    visitor: Annotated[VisitorAuth, Depends(get_auth_visitor)],
):
    state = get_puzzle_state(db, puzzle_name=PUZZLE_NAME, visitor_auth=visitor)
    state["state_access_count"] = state.get("state_access_count", 0) + 1
    set_puzzle_state(db, puzzle_name=PUZZLE_NAME, visitor_auth=visitor, state=state)

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"puzzle": PUZZLE_NAME, "visitor_uid": visitor.uid},
    )
