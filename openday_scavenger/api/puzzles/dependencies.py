from pathlib import Path
from typing import Annotated

from fastapi import Depends, Request, status
from sqlalchemy.orm import Session

from openday_scavenger.api.db import get_db
from openday_scavenger.api.puzzles.service import get_all_responses
from openday_scavenger.api.visitors.dependencies import get_auth_visitor
from openday_scavenger.api.visitors.schemas import VisitorAuth

from .exceptions import DisabledPuzzleError, PuzzleCompletedError, UnknownPuzzleError
from .models import Puzzle


async def get_puzzle_name_from_request(request: Request, db: Annotated["Session", Depends(get_db)]):
    """
    Extracts the puzzle name from the request URL path and returns it.

    Args:
        request (Request): The incoming HTTP request.
        db (Annotated["Session", Depends(get_db)]): The database session dependency.

    Returns:
        str: The name of the puzzle extracted from the URL path.

    Raises:
        UnknownPuzzleError: If a valid puzzle name is not found in the URL path.

    Example:
        If the request URL is 'http://example.com/puzzles/demo',
        the function will return 'demo'.
    """

    try:
        path_parts = Path(request.url.path).parts
        puzzle_name = path_parts[path_parts.index("puzzles") + 1]
    except (ValueError, IndexError):
        raise UnknownPuzzleError(
            status_code=status.HTTP_404_NOT_FOUND, detail="URL doesn't contain valid puzzle path."
        )
    return puzzle_name


async def block_disabled_puzzles(
    request: Request,
    db: Annotated["Session", Depends(get_db)],
    puzzle_name: Annotated[str, Depends(get_puzzle_name_from_request)],
):
    """Dependency that prevents access to unknown or disabled puzzle endpoints"""
    # Use the pathlib library to deconstruct the url and find the name of the puzzle
    # In order to allow multi-level paths, we search for the path component after the "puzzles"
    # component in the route.

    # Look up the puzzle in the database. If the puzzle has not been registered in the database
    # raise an unknown puzzle exception. If it has been disabled raise the disabled puzzle exception.
    puzzle = db.query(Puzzle).filter(Puzzle.name == puzzle_name).first()

    if puzzle is None:
        raise UnknownPuzzleError(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No puzzle with the name {puzzle_name} is registered in the database",
        )

    if not puzzle.active:
        raise DisabledPuzzleError(status_code=status.HTTP_403_FORBIDDEN, detail="Disabled Puzzle")


async def block_correctly_answered_puzzle(
    request: Request,
    db: Annotated["Session", Depends(get_db)],
    visitor: Annotated[VisitorAuth | None, Depends(get_auth_visitor)],
):
    """
    Blocks a puzzle if the visitor has already answered it correctly.

    Args:
        request (Request): The HTTP request object.
        db (Session): The SQLAlchemy database session.
        visitor (VisitorAuth | None): The authenticated visitor, or None if not authenticated.

    Raises:
        UnknownPuzzleError: If the puzzle is not found.
        PuzzleCompletedError: If the visitor has already answered the puzzle correctly.
    """

    if visitor is None:
        return

    try:
        path_parts = Path(request.url.path).parts
        puzzle_name = path_parts[path_parts.index("puzzles") + 1]
    except (ValueError, IndexError):
        raise UnknownPuzzleError(status_code=status.HTTP_404_NOT_FOUND, detail="Unknown Puzzle")

    responses = get_all_responses(
        db, filter_by_puzzle_name=puzzle_name, filter_by_visitor_uid=visitor.uid
    )
    if any([response.is_correct for response in responses]):
        raise PuzzleCompletedError(status_code=status.HTTP_410_GONE, detail="Puzzle Completed")
