import json
from typing import List

from sqlalchemy.orm import Session

from openday_scavenger.api.puzzles.service import get_all

from .schemas import MapCoordinate

__all__ = ("get_map_locations",)


def get_map_locations(db_session: Session) -> List[MapCoordinate]:
    """
    Return all puzzle locations.

    Args:
        db_session (Session): The SQLAlchemy session object.

    Returns:
        List of map location objects entered as the location of puzzles
    """
    # Get "map" puzzle answer which contains the pixel co-ordinates of puzzle locations
    puzzles = get_all(db_session=db_session, only_active=True)

    location_arrays = [p.location for p in puzzles if p.location]

    locations: List[MapCoordinate] = []

    for l_array in location_arrays:
        puzzle_locations = json.loads(l_array)
        for loc in puzzle_locations:
            locations.append(loc)

    return locations
