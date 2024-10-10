from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from openday_scavenger.api.db import get_db
from openday_scavenger.api.puzzles.service import get_puzzle_state, set_puzzle_state
from openday_scavenger.api.visitors.dependencies import get_auth_visitor
from openday_scavenger.api.visitors.schemas import VisitorAuth

PUZZLE_NAME = "imagereveal"
MATCHES = [5, 1, 2, 4]
FRACTIONS = [1, 5, 9, 10]
INITIAL_GUESSES = 6

router = APIRouter()
templates = Jinja2Templates(directory=Path(__file__).resolve().parent / "static")


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
    # We demonstrate the use of state by incrementing a counter each time a user
    # access this puzzle endpoint.
    # Use this to store any intermediate state of the visitor while completing a puzzle.
    state = get_puzzle_state(db, puzzle_name=PUZZLE_NAME, visitor_auth=visitor)
    state["complete"] = False
    state["state_access_count"] = state.get("state_access_count", 0) + 1
    state["correct_guesses"] = state.get("correct_guesses", 0)
    state["remaining_guesses"] = state.get("remaining_guesses", INITIAL_GUESSES)
    state["animal_id"] = state.get("animal_id", 1)
    state["fraction"] = state.get("fraction", FRACTIONS[0])
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
    print("animal", animal)
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"puzzle": PUZZLE_NAME, "state": state},
    )


# @router.post("/partsubmission")
# async def partsubmission(
#     animal: Annotated[str, Form()],
#     request: Request,
#     db: Annotated["Session", Depends(get_db)],
#     visitor: Annotated[VisitorAuth, Depends(get_auth_visitor)],
# ):
#     # We demonstrate the use of state by incrementing a counter each time a user
#     # access this puzzle endpoint.
#     # Use this to store any intermediate state of the visitor while completing a puzzle.
#     state = get_puzzle_state(db, puzzle_name=PUZZLE_NAME, visitor_auth=visitor)
#     animal_id = state.get("animal_id")
#     if animal == animal_id:
#         # correct guess
#         state["correct_guesses"] = state.get("correct_guesses", 0) + 1
#         state["remaining_guesses"] = state.get("remaining_guesses", INITIAL_GUESSES)
#         state["animal_id"] = state.get("animal_id", 1) + 1
#         state["fraction"] = FRACTIONS[0]

#             # Render the puzzle game page
#         return templates.TemplateResponse(
#             request=request,
#             name="inter.html",
#             context={"puzzle": PUZZLE_NAME, "state": state},
#         )
#     else:
#         # incorrect guess
#         pass
#         # state["correct_guesses"] = state.get("correct_guesses", 0)
#         # state["remaining_guesses"] = state.get("remaining_guesses", INITIAL_GUESSES) - 1
#         # if state["remaining_guesses"] < 1:
#         #     # failed to solve puzzle
#         #     # Do something if there are no remaining guesses
#         #     pass
#         # fraction = state.get("fraction", 1)
#         # if fraction < FRACTIONS[-1]:
#         #     next_ix = FRACTIONS.index(fraction) + 1
#         #     fraction = FRACTIONS[next_ix]
#         # else:
#         #     state["animal_id"] = state.get("animal_id", 1)
#         # state["fraction"] = fraction
#     set_puzzle_state(db, puzzle_name=PUZZLE_NAME, visitor_auth=visitor, state=state)

#     # Do something if all animals guessed correctly


#     # Render the puzzle game page
#     return templates.TemplateResponse(
#         request=request,
#         name="index.html",
#         context={"puzzle": PUZZLE_NAME, "state": state},
#     )
