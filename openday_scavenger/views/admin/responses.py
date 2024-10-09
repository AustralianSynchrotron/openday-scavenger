from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from openday_scavenger.api.db import get_db
from openday_scavenger.api.puzzles.schemas import ResponseTestCreate
from openday_scavenger.api.puzzles.service import generate_test_data, get_all_responses

router = APIRouter()

templates = Jinja2Templates(directory=Path(__file__).resolve().parent / "templates")


@router.get("/static/{path:path}")
async def get_static_files(
    path: Path,
):
    """Serve files from a local static folder"""
    # This route is required as the current version of FastAPI doesn't allow
    # the mounting of folders on APIRouter. This is an open issue:
    # https://github.com/fastapi/fastapi/discussions/9070
    parent_path = Path(__file__).resolve().parent / "static"
    file_path = parent_path / path

    # Make sure the requested path is a file and relative to this path
    if file_path.is_relative_to(parent_path) and file_path.is_file():
        return FileResponse(file_path)
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Requested file does not exist"
        )


@router.get("/")
async def render_response_page(request: Request):
    """Render the responses admin page"""
    return templates.TemplateResponse(
        request=request, name="responses.html", context={"active_page": "responses"}
    )


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


@router.post("/test")
async def add_test_entries(
    db: Annotated["Session", Depends(get_db)],
    response_test_in: Annotated[ResponseTestCreate, Form()],
):
    generate_test_data(
        db,
        number_visitors=response_test_in.number_visitors,
        number_wrong_answers=response_test_in.number_wrong_answers,
    )

    return {"success": True}
