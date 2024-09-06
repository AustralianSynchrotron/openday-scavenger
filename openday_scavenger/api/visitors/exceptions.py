class VisitorExistsError(RuntimeError):
    """Raised during visitor creation if its uid already exists"""

    pass


class VisitorUIDInvalidError(RuntimeError):
    """Raised during visitor creation if its uid already exists"""

    pass


class VisitorNotAuthenticatedError(RuntimeError):
    """Raised if a visitor tries to access a protected page and is not authenticated"""

    pass
