from pathlib import Path
from typing import Annotated
from fastapi import Request, Depends, status
from sqlalchemy.orm import Session

from openday_scavenger.api.db import get_db
from .models import Puzzle
from .exceptions import UnknownPuzzleError, DisabledPuzzleError


async def block_disabled_puzzles(request: Request, db: Annotated["Session", Depends(get_db)]):
    """ Dependency that prevents access to unknown or disabled puzzle endpoints """
    # Use the pthlib library to deconstruct the url and get the final path component
    puzzle_name = Path(request.url.path).name

    # Look up the puzzle in the database. If the puzzle has not been registered in the database
    # raise an unknown puzzle exception. If it has been disabled raise the disabled puzzle exception.
    puzzle = db.query(Puzzle).filter(Puzzle.name == puzzle_name).first()
    
    if puzzle is None:
        raise UnknownPuzzleError(status_code=status.HTTP_404_NOT_FOUND, detail="Unknown Puzzle")
    
    if not puzzle.active:
        raise DisabledPuzzleError(status_code=status.HTTP_403_FORBIDDEN, detail="Disabled Puzzle")
