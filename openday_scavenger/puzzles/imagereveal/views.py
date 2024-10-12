from copy import deepcopy
from functools import lru_cache
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from openday_scavenger.api.db import get_db
from openday_scavenger.api.puzzles.service import get as get_puzzle
from openday_scavenger.api.puzzles.service import get_puzzle_state, set_puzzle_state
from openday_scavenger.api.visitors.dependencies import get_auth_visitor
from openday_scavenger.api.visitors.schemas import VisitorAuth

PUZZLE_NAME = "imagereveal"
MATCHES = [5, 1, 2, 4]
FRACTIONS = [1, 5, 9, 10]
INITIAL_GUESSES = 6

router = APIRouter()
templates = Jinja2Templates(directory=Path(__file__).resolve().parent / "static")


@lru_cache()
def get_solution_from_db(db: Session, puzzle_name: str) -> str:
    # ask the database for the solution.
    # Cached so it should only happen infrequently.
    # If we change the solution in the database, this info *will* be stale.
    # TODO: What happens if solution changes halfway through a game?
    # User will definitely be told their selection is wrong...
    p = get_puzzle(db_session=db, puzzle_name=puzzle_name)
    return p.answer


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
    db: Annotated["Session", Depends(get_db)],
    visitor: Annotated[VisitorAuth, Depends(get_auth_visitor)],
):
    # state stores the intermediate state of the visitor while completing a puzzle.
    state = get_puzzle_state(db, puzzle_name=PUZZLE_NAME, visitor_auth=visitor)
    state["complete"] = False
    state["answer"] = 0
    state["state_access_count"] = state.get("state_access_count", 0) + 1
    state["correct_guesses"] = state.get("correct_guesses", 0)
    state["remaining_guesses"] = state.get("remaining_guesses", INITIAL_GUESSES)
    state["animal_id"] = state.get("animal_id", 1)
    state["fraction_ix"] = state.get("fraction_ix", 0)
    state["fraction"] = state.get("fraction", FRACTIONS[0])
    state["reveal"] = 0
    set_puzzle_state(db, puzzle_name=PUZZLE_NAME, visitor_auth=visitor, state=state)

    # Render the puzzle game page
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"puzzle": PUZZLE_NAME, "state": state},
    )


@router.post("/partsubmission")
async def partsubmission(
    animal: Annotated[str, Form()],
    request: Request,
    db: Annotated["Session", Depends(get_db)],
    visitor: Annotated[VisitorAuth, Depends(get_auth_visitor)],
):
    state = get_puzzle_state(db, puzzle_name=PUZZLE_NAME, visitor_auth=visitor)
    animal_id = state.get("animal_id")
    if int(animal) == MATCHES[animal_id - 1]:
        # A correct guess
        state["correct_guesses"] = state.get("correct_guesses", 0) + 1
        state["remaining_guesses"] = state.get("remaining_guesses", INITIAL_GUESSES)
        state["fraction_ix"] = 0
        state["fraction"] = FRACTIONS[0]
        if animal_id == MATCHES[-1]:
            # Last animal guessed correctly; submit puzzle
            state["complete"] = True
            state["answer"] = get_solution_from_db(db, puzzle_name=PUZZLE_NAME)
            # Set reveal to last animal
            state["reveal"] = state.get("animal_id", 1)
        else:
            # Set reveal to current animal
            state["reveal"] = state.get("animal_id", 1)
            # Set question to next animal
            state["animal_id"] = state.get("animal_id", 1) + 1

        set_puzzle_state(db, puzzle_name=PUZZLE_NAME, visitor_auth=visitor, state=state)

        # Render the puzzle game page
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={"puzzle": PUZZLE_NAME, "state": state},
        )
    else:
        # An incorrect guess
        state["correct_guesses"] = state.get("correct_guesses", 0)
        state["remaining_guesses"] = state.get("remaining_guesses", INITIAL_GUESSES) - 1
        # Set no reveal
        state["reveal"] = 0
        if state["remaining_guesses"] < 1:
            # failed to solve puzzle
            # Do something if there are no remaining guesses
            state["complete"] = True
            state["answer"] = 0

        fraction_ix = state.get("fraction_ix", 0)
        if fraction_ix + 1 < len(FRACTIONS):
            # Increment fraction shown
            fraction_ix += 1
            fraction = FRACTIONS[fraction_ix]
            state["fraction_ix"] = fraction_ix
            state["fraction"] = fraction
        else:
            state["fraction_ix"] = len(FRACTIONS) - 1
            state["fraction"] = FRACTIONS[-1]

        if state["complete"]:
            blank_state = deepcopy(state)
            blank_state["complete"] = False
            blank_state["answer"] = 0
            blank_state["state_access_count"] = 0
            blank_state["correct_guesses"] = 0
            blank_state["remaining_guesses"] = INITIAL_GUESSES
            blank_state["animal_id"] = 1
            blank_state["fraction_ix"] = 0
            blank_state["fraction"] = FRACTIONS[0]
            blank_state["reveal"] = 0
            set_puzzle_state(db, puzzle_name=PUZZLE_NAME, visitor_auth=visitor, state=blank_state)
        else:
            set_puzzle_state(db, puzzle_name=PUZZLE_NAME, visitor_auth=visitor, state=state)

        # Render the puzzle game page
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={"puzzle": PUZZLE_NAME, "state": state},
        )
