import json
from functools import lru_cache
from pathlib import Path
from typing import Annotated, Union

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.logger import logger
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from openday_scavenger.api.db import get_db
from openday_scavenger.api.puzzles.dependencies import get_puzzle_name
from openday_scavenger.api.puzzles.exceptions import DisabledPuzzleError
from openday_scavenger.api.puzzles.service import get
from openday_scavenger.api.visitors.dependencies import get_auth_visitor
from openday_scavenger.api.visitors.schemas import VisitorAuth


def warning_text_no_wordsearch() -> None:
    """Warning text when word_search_generator has not been installed"""
    print("-----------------------------------")
    print("WARNING: Word search generator has not been installed.")
    print("This package is needed to run the word finder (treasure hunt) puzzle.")
    print("Run `uv sync --extra finder` to include the word search generator.")
    print("Run `uv sync --all-extras` to include all extras.")
    print("-----------------------------------")


# import word search generator if available
WORD_SERACH_AVAILABLE = False
try:
    from word_search_generator import WordSearch, utils

    WORD_SERACH_AVAILABLE = True
except ImportError:
    WordSearch = None
    warning_text_no_wordsearch()


router = APIRouter()

templates = Jinja2Templates(directory=Path(__file__).resolve().parent / "templates")

PUZZLE_DEFAULT = "beam,light,magnet,xray"

# Default headings for each puzzle
PUZZLE_MAP = {
    "as": "the Synchrotron",
    "mx": "Macromolecular Crystallography (MX)",
    "mct": "Micro-Computed Tomography",
    "mex": "the Medium Energy XAS (MEX) beamlines",
    "xas": "X-ray Absorption Spectroscopy (XAS)",
    "xfm": "X-ray Fluorescence Microscopy (XFM)",
    "nano": "the Nanoprobe (NANO)",
}

# prepare puzzle routes
puzzle_routes = [f"/treasure_{k}" for k in PUZZLE_MAP.keys()]


def get_quiz(puzzle_name: str, words: list) -> str:
    _, puzzle_key = puzzle_name.split("_")
    return f"There are {len(words)} words related to {PUZZLE_MAP[puzzle_key]}."


def get_puzzle_data(
    ws: Union[WordSearch, None], solution: bool = False, format: str = "dict"
) -> dict | str:
    """Write puzzle data to dict or JSON format.

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
    if format == "json":
        data = json.dumps(data)
    return data


def generate_puzzle(words: list) -> tuple:
    """
    Create a new word search puzzle based on the puzzle name
    """
    # Get the puzzle data
    ww = ", ".join([w for w in words])
    puzzle_dim = max(*[len(w) for w in words], 6) + 1

    # Generate a new word search puzzle
    ws = WordSearch(words=ww, size=puzzle_dim)

    # get puzzle data
    dd = get_puzzle_data(ws)  # solution hidden
    ds = get_puzzle_data(ws, solution=True)  # solution shown

    return dd, ds


""" fetch puzzle data """


@lru_cache
def fetch_puzzle(words: list) -> tuple:
    """
    Fetch puzzle data for puzzle name

    Args:
        words (list): word list to generate the puzzle

    Returns:
        tuple: tuple with puzzle data and solution
    """
    # make sure words is a list otherwise return default
    words = [w for w in words if w]
    if not words:
        words = PUZZLE_DEFAULT.split(",")

    return generate_puzzle(words)


def get_solution_from_db(puzzle_name: str, db_session: Session) -> list:
    """
    Get the puzzle solution from the database session
    and return it as a list of words.

    Args:
        puzzle_name (str): puzzle name (entry in the database)
        db_session (Session): db session

    Returns:
        list: list of words
    """
    try:
        solution = get(db_session, puzzle_name).answer
    except Exception as e:
        solution = PUZZLE_DEFAULT
        logger.warning(
            e,
            f"Puzzle name {puzzle_name} not found.",
            f"Using default solution: {solution}",
        )

    # create word list
    words = []
    for word in solution.split(","):
        words.append(str(word))

    return words


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
    request: Request,
    puzzle_name: Annotated[str, Depends(get_puzzle_name)],
    visitor: Annotated[VisitorAuth, Depends(get_auth_visitor)],
    db_session: Annotated["Session", Depends(get_db)],
):
    """
    Main endpoint for finder puzzle.
    Gets the word list from the database, fetches the puzzle data,
    returns the puzzle question and the puzzle data.

    Args:
        request (Request): Request object
        puzzle_name (str): puzzle name from database
        visitor (VisitorAuth): visitor token
        db_session (Session): db session

    Returns:
        Response: response object with puzzle data
    """

    # Get puzzle name, word list, data and metadata
    if not WORD_SERACH_AVAILABLE:
        warning_text_no_wordsearch()
        raise DisabledPuzzleError(status_code=status.HTTP_403_FORBIDDEN)

    solution = get_solution_from_db(puzzle_name, db_session)
    data, data_as_solution = fetch_puzzle(words=tuple(solution))
    question = get_quiz(puzzle_name, solution)

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "puzzle": puzzle_name,
            "question": question,
            "data": data,
            "data_as_solution": data_as_solution,
        },
    )
