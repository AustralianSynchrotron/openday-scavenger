from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.exception_handlers import http_exception_handler
from fastapi.logger import logger
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException

from openday_scavenger.api.db import create_tables
from openday_scavenger.api.puzzles.dependencies import block_disabled_puzzles
from openday_scavenger.api.puzzles.exceptions import (
    DisabledPuzzleError,
    UnknownPuzzleError,
)
from openday_scavenger.api.visitors.dependencies import auth_required
from openday_scavenger.api.visitors.exceptions import (
    VisitorNotAuthenticatedError,
    VisitorUIDInvalidError,
)
from openday_scavenger.puzzles import router as puzzle_router
from openday_scavenger.views.admin import router as admin_router
from openday_scavenger.views.game.game import router as game_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables at startup
    create_tables()
    yield
    # If we wanted to to add something when the app is shutdown,
    # it could be added here


app = FastAPI(
    title="Open Day Scavenger Hunt",
    description="blablabla",
    openapi_url="",
    lifespan=lifespan,
)


@app.exception_handler(VisitorNotAuthenticatedError)
async def visitor_auth_exception_handler(request, exc):
    """Catch an authenticated user exception and send them to the start page"""
    logger.error(f"{request.url} {str(exc)}", exc_info=exc)
    return RedirectResponse("/")


@app.exception_handler(VisitorUIDInvalidError)
async def visitor_uid_invalid_exception_handler(request, exc):
    """Catch an invalid uid"""
    logger.error(f"{request.url} {str(exc)}", exc_info=exc)
    templates = Jinja2Templates(directory=Path(__file__).resolve().parent / "static" / "html")
    return templates.TemplateResponse(request=request, name="404_invalid_uid.html")


@app.exception_handler(UnknownPuzzleError)
async def unknown_puzzle_exception_handler(request, exc):
    """Catch an unknown puzzle exception and render the relevant page"""
    logger.error(f"{request.url} {str(exc)}\n{exc.detail}", exc_info=exc)
    templates = Jinja2Templates(directory=Path(__file__).resolve().parent / "static" / "html")
    return templates.TemplateResponse(request=request, name="404_unknown_puzzle.html")


@app.exception_handler(DisabledPuzzleError)
async def disabled_puzzle_exception_handler(request, exc):
    """Catch a disabled puzzle exception and render the relevant page"""
    logger.error(f"{request.url} {str(exc)}\n{exc.detail}", exc_info=exc)
    templates = Jinja2Templates(directory=Path(__file__).resolve().parent / "static" / "html")
    return templates.TemplateResponse(request=request, name="403_disabled_puzzle.html")


@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request, exc):
    """Catch HTTP exceptions, log the error and if it is a 404 render the 404 template"""
    templates = Jinja2Templates(directory=Path(__file__).resolve().parent / "static" / "html")
    logger.error(f"{request.url} {str(exc)}\n{exc.detail}", exc_info=exc)

    match exc.status_code:
        case status.HTTP_404_NOT_FOUND:
            return templates.TemplateResponse(request=request, name="404_general.html")

    detail = exc.detail if isinstance(exc.detail, str) else exc.detail.dict()
    headers = exc.headers if hasattr(exc, "headers") else None

    return await http_exception_handler(
        request,
        HTTPException(status_code=exc.status_code, detail=detail, headers=headers),
    )


# Mount the static folder to serve common assets
app.mount(
    "/static",
    StaticFiles(directory=Path(__file__).resolve().parent / "static"),
    name="static",
)

# Include routes
app.include_router(game_router, prefix="")
app.include_router(admin_router, prefix="/admin")
app.include_router(
    puzzle_router,
    prefix="/puzzles",
    dependencies=[Depends(block_disabled_puzzles), Depends(auth_required)],
)
