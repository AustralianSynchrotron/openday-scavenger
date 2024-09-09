from fastapi import HTTPException


class UnknownPuzzleError(HTTPException):
    """Raised if the user tries to access a puzzle with an unknown name"""

    pass


class DisabledPuzzleError(HTTPException):
    """Raised if the user tries to access a puzzle that has been disabled"""

    pass


class PuzzleCreationError(RuntimeError):
    """Raised if the creation of a new puzzle entry in the database failed"""

    pass


class PuzzleUpdatedError(RuntimeError):
    """Raised if the modification of new puzzle entry in the database failed"""

    pass


class PuzzleNotFoundError(RuntimeError):
    """Raised if a puzzle cannot be found in the database"""

    pass
