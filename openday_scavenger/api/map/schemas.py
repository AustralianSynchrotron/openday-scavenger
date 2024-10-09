from typing import List

from pydantic import BaseModel


class MapCoordinate(BaseModel):
    """Top & left coordinate for map marker"""

    top: float
    left: float


class MapLocations(BaseModel):
    """List of map coordinates"""

    locations: List[MapCoordinate]
