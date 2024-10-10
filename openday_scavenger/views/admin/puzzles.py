import json
import typing
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response, UploadFile, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from openday_scavenger.api.db import get_db
from openday_scavenger.api.puzzles.schemas import PuzzleCreate, PuzzleUpdate
from openday_scavenger.api.puzzles.service import (
    create,
    generate_puzzle_qr_code,
    generate_puzzle_qr_codes_pdf,
    get,
    get_all,
    update,
)
from openday_scavenger.config import get_settings

router = APIRouter()
config = get_settings()
templates = Jinja2Templates(directory=Path(__file__).resolve().parent / "templates")


# The puzzle JSON dumps might need to be editable by humans
# and its easier to have it formatted by default
# Avoid using this for endpoints that are used often as it is a blocking operation
class PrettyJSONResponse(Response):
    media_type = "application/json"

    def render(self, content: typing.Any) -> bytes:
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=2,
            separators=(", ", ": "),
        ).encode("utf-8")


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
async def render_puzzle_page(request: Request):
    """Render the puzzle admin page"""
    return templates.TemplateResponse(
        request=request, name="puzzles.html", context={"active_page": "puzzles"}
    )


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


@router.get("/{puzzle_name}/edit_modal")
async def render_puzzle_edit_modal(
    puzzle_name: str, request: Request, db: Annotated["Session", Depends(get_db)]
):
    """Render the edit modal for puzzle entries on the admin page"""
    puzzle = get(db, puzzle_name=puzzle_name)

    return templates.TemplateResponse(
        request=request,
        name="puzzles_edit_modal.html",
        context={"puzzle": puzzle},
    )


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


@router.get("/download-json")
async def download_json(db: Annotated["Session", Depends(get_db)]):
    puzzles = get_all(db)

    return PrettyJSONResponse(
        {"puzzles": jsonable_encoder(puzzles)},
        headers={"Content-Disposition": "attachment; filename=puzzle_data.json"},
    )


@router.post("/upload-json")
async def upload_json(
    request: Request, file: UploadFile, db: Annotated["Session", Depends(get_db)]
):
    file_contents = await file.read()
    parsed_file = json.loads(file_contents)

    if not isinstance(parsed_file, dict) or type(parsed_file["puzzles"]) is not list:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="JSON file must be in valid format"
        )

    existing_puzzles_by_id = {item.id: item for item in get_all(db)}

    for puzzle in parsed_file["puzzles"]:
        existing_puzzle = existing_puzzles_by_id[puzzle["id"]]
        if existing_puzzle:
            _ = update(db, existing_puzzle.name, PuzzleUpdate(**puzzle))
        else:
            _ = create(db, PuzzleCreate(**puzzle))

    return await _render_puzzles_table(request, db)
