import json
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates

from word_search_generator import WordSearch, utils

from openday_scavenger.api.visitors.dependencies import get_auth_visitor
from openday_scavenger.api.visitors.schemas import VisitorAuth

router = APIRouter()

templates = Jinja2Templates(directory=Path(__file__).resolve().parent / "templates")


def get_puzzle_data(
    ws: WordSearch,
    solution: bool = False,
    format: str = 'dict'
) -> dict|str:
    """Write current puzzle to dict or JSON format.

    Args:
        path (Path): Path to write the file to.
        ws (WordSearch): Current Word Search puzzle.
        solution (bool, optional): Only include the puzzle solution. Defaults to False.

    Returns:
        Path: Final save path.
    """
    puzzle = utils.hide_filler_characters(ws) if solution else ws.cropped_puzzle
    data = {
            "puzzle": puzzle,
            "words": [word.text for word in ws.placed_words],
            "key": {word.text: word.key_info_json for word in ws.words if word.placed},
        }
    if format == 'json':
        data = json.dumps(data)
    return data


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


# function to create and return the finder puzzle
@router.get("/new_finder")
async def new_finder(
    request: Request,
    visitor: Annotated[VisitorAuth | None, Depends(get_auth_visitor)],
):
    # create the finder puzzle
    puzzle_dim = 10 # puzzle size

    # word list - eventually get this from a file
    words = ["dog", "cat", "pig", "horse", "donkey", "turtle", "goat", "sheep"]
    ww = ", ".join([w for w in words])

    # Generate a new word search puzzle
    ws = WordSearch(words = ww, size = puzzle_dim)

    # get puzzle data
    dd = get_puzzle_data(ws) # solution hidden
    ds = get_puzzle_data(ws, solution=True) # solution shown

    # send the puzzle data to the template
    return templates.TemplateResponse(
        request=request,
        name="finder_words.html",
        context={
            "data": dd,
            "solution": ds,
        },
    )


# function to test the new finder endpoint
@router.get("/test_new_finder")
async def test_new_finder(
    request: Request,
    visitor: Annotated[VisitorAuth | None, Depends(get_auth_visitor)],
):
    # create the finder puzzle
    puzzle_dim = 10 # puzzle size

    # word list - eventually get this from a file
    words = ["dog", "cat", "pig", "horse", "donkey", "turtle", "goat", "sheep"]

    # start with example data
    dd = {
        "puzzle": [
            ["A", "B", "C", "D", "E"],
            ["F", "G", "H", "I", "J"],
            ["K", "L", "M", "N", "O"],
            ["P", "Q", "R", "S", "T"],
            ["U", "V", "W", "X", "Y"],
        ],
        "words": words
    }

    ds = {
        "puzzle": [
            [" ", " ", "C", "D", "E"],
            [" ", " ", "H", "I", "J"],
            ["K", " ", "M", " ", "O"],
            ["P", "Q", "R", "S", "T"],
            [" ", "V", "W", " ", " "],
        ],
        "words": words
    }

    # send the puzzle data to the template
    return templates.TemplateResponse(
        request=request,
        name="finder_words.html",
        context={
            "data": dd,
            "solution": ds,
        },
    )


@router.get("/")
async def index(request: Request, visitor: Annotated[VisitorAuth, Depends(get_auth_visitor)]):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"puzzle": "finder", "visitor": visitor.uid},
    )
