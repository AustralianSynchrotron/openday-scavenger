import random
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates

from openday_scavenger.api.visitors.dependencies import get_auth_visitor
from openday_scavenger.api.visitors.schemas import VisitorAuth

router = APIRouter()

templates = Jinja2Templates(directory=Path(__file__).resolve().parent / "templates")

INITIAL_WORD = "PROBATIONS"  # not the solution, but an anagram of it :D


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


# function that returns a shuffled version of the word
@router.get("/shuffled")
async def shuffle_word(
    request: Request,
    visitor: Annotated[VisitorAuth | None, Depends(get_auth_visitor)],
):
    # create a shuffled version of the word
    word = "".join(random.sample(INITIAL_WORD, len(INITIAL_WORD)))
    return templates.TemplateResponse(
        request=request,
        name="scrambled_word.html",
        context={
            "scrambled_word": word,
        },
    )


@router.get("/")
async def index(
    request: Request, visitor: Annotated[VisitorAuth | None, Depends(get_auth_visitor)]
):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "puzzle": "shuffleanagram",
            "visitor": visitor.uid,
            "scrambled_word": INITIAL_WORD,
        },
    )
