from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from openday_scavenger.api.db import get_db
from openday_scavenger.api.visitors.dependencies import get_auth_visitor
from openday_scavenger.api.visitors.schemas import VisitorAuth

from .exceptions import GameOverException, PuzzleSolvedException
from .service import PUZZLE_NAME, PuzzleStatus, get_status, reset_status, set_status

router = APIRouter()

templates = Jinja2Templates(
    directory=Path(__file__).resolve().parent / "templates",
)


@router.get("/static/{path:path}")
async def get_static_files(
    path: Path,
):
    """get_static_files Serve files from a local static folder"""
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
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requested file does not exist",
        )


@router.get("/shuffled")
async def get_shuffled_words(
    request: Request,
    visitor: Annotated[VisitorAuth, Depends(get_auth_visitor)],
    status: Annotated[PuzzleStatus, Depends(get_status)],
    db: Annotated["Session", Depends(get_db)],
):
    """get_shuffled_words shuffle the words in the puzzle"""
    status.shuffle_words()
    status = await set_status(
        status,
        visitor=visitor,
        db=db,
    )

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "puzzle": PUZZLE_NAME,
            "status": status,
        },
    )


@router.delete("/selection")
async def deselect_all_words(
    request: Request,
    visitor: Annotated[VisitorAuth, Depends(get_auth_visitor)],
    status: Annotated[PuzzleStatus, Depends(get_status)],
    db: Annotated["Session", Depends(get_db)],
):
    """deselect_all_words Deselect all the words"""
    status.deselect_all_words()
    status = await set_status(
        status,
        visitor=visitor,
        db=db,
    )

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "puzzle": PUZZLE_NAME,
            "status": status,
        },
    )


@router.put("/{word_id}/selection")
async def toggle_word_selection(
    word_id: str,
    request: Request,
    visitor: Annotated[VisitorAuth, Depends(get_auth_visitor)],
    status: Annotated[PuzzleStatus, Depends(get_status)],
    db: Annotated["Session", Depends(get_db)],
):
    """toggle_word_selection Toggle the selection of a word"""
    try:
        status.toggle_word_selection(word_id)
        msg = None
    except Exception as e:
        msg = str(e)

    status = await set_status(
        status,
        visitor=visitor,
        db=db,
    )

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "puzzle": PUZZLE_NAME,
            "status": status,
            "message": msg,
        },
    )


@router.post("/selection-submission")
async def submit_selection(
    request: Request,
    visitor: Annotated[VisitorAuth, Depends(get_auth_visitor)],
    status: Annotated[PuzzleStatus, Depends(get_status)],
    db: Annotated["Session", Depends(get_db)],
):
    """submit_selection Submit the selection of words"""
    msg = None
    game_over = False
    register_success = False
    try:
        status.submit_selection()
    except GameOverException as e:
        msg = str(e)
        game_over = True
    except PuzzleSolvedException as e:
        msg = str(e)
        register_success = True
    except Exception as e:
        msg = str(e)

    status = await set_status(
        status,
        visitor=visitor,
        db=db,
    )

    # Remove the status of the visitor after the puzzle is solved
    # This is only done if the sessions are disabled
    if (visitor.uid is None) and register_success:
        await reset_status(
            visitor=visitor,
            db=db,
        )

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "puzzle": PUZZLE_NAME,
            "status": status,
            "message": msg,
            "game_over": game_over,
            "register_success": register_success,
        },
    )


@router.delete("/")
async def reset(
    request: Request,
    clean_status: Annotated[PuzzleStatus, Depends(reset_status)],
):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "puzzle": PUZZLE_NAME,
            "status": clean_status,
        },
    )


@router.get("/")
async def index(
    request: Request,
    status: Annotated[PuzzleStatus, Depends(get_status)],
):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "puzzle": PUZZLE_NAME,
            "status": status,
        },
    )
