import secrets
from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from openday_scavenger.config import get_settings

from .admin import router as admin_router
from .puzzles import router as puzzle_router
from .responses import router as response_router
from .visitors import router as visitor_router

config = get_settings()

security = HTTPBasic()


def credential_check(credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    """
    Verify the provided credentials against the stored admin username and password.

    Args:
        credentials (Annotated[HTTPBasicCredentials, Depends(security)]):
            The HTTP basic credentials provided by the user.

    Raises:
        HTTPException: If the username or password is incorrect, an HTTP 401 Unauthorized
            exception is raised with aM message and appropriate headers.
    """

    if not config.ADMIN_AUTH_ENABLED:
        return

    current_username_bytes = credentials.username.encode("utf8")
    is_correct_username = secrets.compare_digest(
        current_username_bytes, config.ADMIN_USER.encode("utf8")
    )
    current_password_bytes = credentials.password.encode("utf8")
    is_correct_password = secrets.compare_digest(
        current_password_bytes, config.ADMIN_PASSWORD.encode("utf8")
    )
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )


router = APIRouter(dependencies=[Depends(credential_check)])

router.include_router(admin_router, prefix="")
router.include_router(puzzle_router, prefix="/puzzles")
router.include_router(visitor_router, prefix="/visitors")
router.include_router(response_router, prefix="/responses")
