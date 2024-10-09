import json

from sqlalchemy.orm import Session

from openday_scavenger.api.puzzles.service import get

from .schemas import MapLocations

__all__ = ("get_map_locations",)


def get_map_locations(db_session: Session) -> MapLocations:
    """
    Return stored map 'puzzle' locations array string.

    Args:
        db_session (Session): The SQLAlchemy session object.

    Returns:
        List of map location objects entered as the answer of map 'puzzle'
    """
    # Get "map" puzzle answer which contains the pixel co-ordinates of puzzle locations
    puzzle = get(db_session, "map")
    locations = json.loads(puzzle.answer)
    return locations
