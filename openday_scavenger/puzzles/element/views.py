import json
import random
import re
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates

from openday_scavenger.api.visitors.dependencies import get_auth_visitor
from openday_scavenger.api.visitors.schemas import VisitorAuth

from .services import get_category_style, get_options_less, get_options_more, get_questions

router = APIRouter()

templates = Jinja2Templates(directory=Path(__file__).resolve().parent / "templates")

# Load element_list
with open(Path(__file__).resolve().parent / "static" / "data" / "element_list.json") as f:
    elements = json.load(f)

# Load element_lookup map
with open(Path(__file__).resolve().parent / "static" / "data" / "element_lookup.json") as f:
    element_lookup = json.load(f)


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
async def index(
    request: Request, visitor: Annotated[VisitorAuth | None, Depends(get_auth_visitor)]
):
    # Get the path from the request and extract the suffix
    path = request.url.path
    puzzle_name = path.split("/")[-2] if path.endswith("/") else path.split("/")[-1]
    suffix = re.sub(r"/$", "", puzzle_name.split("_")[-1])

    # Get questions and hints based on the path
    questions = get_questions(suffix)
    options_less = get_options_less(suffix)
    options_more = get_options_more(suffix)

    # choose a random question
    question = random.choice(questions)

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "puzzle": puzzle_name,
            "visitor": visitor.uid,
            "location": suffix.upper(),
            "elements": elements,
            "element_lookup": element_lookup,
            "get_category_style": get_category_style,
            "question": question,
            "options_less": options_less,
            "options_more": options_more,
        },
    )
