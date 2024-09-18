import json
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates

from openday_scavenger.api.visitors.dependencies import get_auth_visitor
from openday_scavenger.api.visitors.schemas import VisitorAuth

from word_search_generator import WordSearch, utils
"""
# NOTE: LS needed to install these binaries on my mac
# for word_searh_generator pillow dependency to work
# brew install libtiff libjpeg webp little-cms2brew install libtiff libjpeg webp little-cms2
# from this post:
# https://stackoverflow.com/questions/44043906/the-headers-or-library-files-could-not-be-found-for-jpeg-installing-pillow-on
"""

router = APIRouter()

templates = Jinja2Templates(directory=Path(__file__).resolve().parent / "templates")


# define puzzle quiz and word lists
PuzzleQuiz = {
    "synch_finder": {
        "question": "Can you find all the words related to the Synchrotron?",
        "words": ["synchrotron", "beamline", "magnet", "xrays", "lightsource", "accelerator"],
    },
    "mx3_finder": {
        "question": "Can you find all the words related to Macromolecular Crystallography?",
        "words": ["high", "performance", "microfocus", "crystals", "protein"],
    },
    "mct_finder": {
        "question": "Can you find all the words related to Micro-Computed Tomography?",
        "words": ["monochromatic", "pink", "white", "xray", "beams", "structures", "spatial", "resolution"],
    },
    "mex_finder": {
        "question": "Can you find all the words related to the Medium Energy X-ray (MEX) beamlines?",
        "words": ["soft", "hard", "xray", "tuneable", "microprobe", "routine", "spectroscopy"],
    },
    "xas_finder": {
        "question": "Can you find all the words related to the X-ray Absorption Spectroscopy (XAS) beamline?",
        "words": ["absorption", "transmission", "fluorescence", "monochromater", "oxidation", "photons"],
    },
}


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


def create_puzzle(path: Path):
    
    # word list and question from puzzle dictionary
    puzzle_name = path.name 
    question = PuzzleQuiz[puzzle_name]["question"]
    words = PuzzleQuiz[puzzle_name]["words"]
    ww = ", ".join([w for w in words])
    puzzle_dim = max([len(w) for w in words]) 
    
    # Generate a new word search puzzle
    ws = WordSearch(words = ww, size = puzzle_dim)

    # get puzzle data
    dd = get_puzzle_data(ws) # solution hidden
    ds = get_puzzle_data(ws, solution=True) # solution shown

    return question, dd, ds


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
async def index(request: Request, visitor: Annotated[VisitorAuth, Depends(get_auth_visitor)]):
    question, data, data_as_solution = create_puzzle(Path(request.url.path) )

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "puzzle": "finder",
            "visitor": visitor.uid,
            "question": question,
            "data": data,
            "data_as_solution": data_as_solution
        },
    )
