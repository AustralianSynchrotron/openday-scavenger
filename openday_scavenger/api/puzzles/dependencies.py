from pathlib import Path
from typing import Annotated

from fastapi import Depends, Request, status
from sqlalchemy.orm import Session

from openday_scavenger.api.db import get_db

from .exceptions import DisabledPuzzleError, UnknownPuzzleError
from .models import Puzzle


async def block_disabled_puzzles(request: Request, db: Annotated["Session", Depends(get_db)]):
    """Dependency that prevents access to unknown or disabled puzzle endpoints"""
    # Use the pathlib library to deconstruct the url and find the name of the puzzle
    # In order to allow multi-level paths, we search for the path component after the "puzzles"
    # component in the route.
    try:
        path_parts = Path(request.url.path).parts
        puzzle_name = path_parts[path_parts.index("puzzles") + 1]
    except (ValueError, IndexError):
        raise UnknownPuzzleError(status_code=status.HTTP_404_NOT_FOUND, detail="Unknown Puzzle")

    # Look up the puzzle in the database. If the puzzle has not been registered in the database
    # raise an unknown puzzle exception. If it has been disabled raise the disabled puzzle exception.
    puzzle = db.query(Puzzle).filter(Puzzle.name == puzzle_name).first()

    if puzzle is None:
        raise UnknownPuzzleError(status_code=status.HTTP_404_NOT_FOUND, detail="Unknown Puzzle")

    if not puzzle.active:
        raise DisabledPuzzleError(status_code=status.HTTP_403_FORBIDDEN, detail="Disabled Puzzle")
