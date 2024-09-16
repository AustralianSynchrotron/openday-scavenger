class VisitorExistsError(RuntimeError):
    """Raised during visitor creation if its uid already exists"""


class VisitorUIDInvalidError(RuntimeError):
    """Raised if a visitor UID is invalid"""


class VisitorNotAuthenticatedError(RuntimeError):
    """Raised if a visitor tries to access a protected page and is not authenticated"""
