from fastapi import HTTPException


class UnknownPuzzleError(HTTPException):
    """ Raised if the user tries to access a puzzle with an unknown name """
    pass


class DisabledPuzzleError(HTTPException):
    """ Raised if the user tries to access a puzzle that has been disabled """
    pass
