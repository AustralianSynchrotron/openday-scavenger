from pydantic import BaseModel


class MapCoordinate(BaseModel):
    """Top & left coordinate for map marker"""

    top: float
    left: float
