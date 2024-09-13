from fastapi import HTTPException


class UnknownPuzzleError(HTTPException):
    """Raised if the user tries to access a puzzle with an unknown name"""


class DisabledPuzzleError(HTTPException):
    """Raised if the user tries to access a puzzle that has been disabled"""


class PuzzleCreationError(RuntimeError):
    """Raised if the creation of a new puzzle entry in the database failed"""


class PuzzleUpdatedError(RuntimeError):
    """Raised if the modification of new puzzle entry in the database failed"""


class PuzzleNotFoundError(RuntimeError):
    """Raised if a puzzle cannot be found in the database"""


class ForbiddenAccessTestEndpointError(RuntimeError):
    """Raised of somebidy tries to access the test endpoint if it is turned off"""
