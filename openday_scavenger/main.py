from typing import Annotated
from pathlib import Path
from sqlalchemy.orm import Session
from fastapi import FastAPI, Depends, Request, HTTPException, status
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from openday_scavenger.api.db import get_db
from openday_scavenger.api.puzzles.models import Puzzle

from openday_scavenger.api.db import create_tables
from openday_scavenger.puzzles import router as puzzle_router
from openday_scavenger.views.game.game import router as game_router
from openday_scavenger.views.admin import router as admin_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables at startup
    create_tables()
    yield
    # If we wanted to to add something when the app is shutdown,
    # it could be added here


app = FastAPI(
    title='Open Day Scavenger Hunt',
    description='blablabla',
    openapi_url='',
    lifespan=lifespan
)

# @app.exception_handler(StarletteHTTPException)
# async def custom_http_exception_handler(request, exc):
#     ''' Catch any HTTPException and log the error '''
#     logger.error(f'{str(exc)}\n{exc.detail}', exc_info=exc)

#     detail = exc.detail if isinstance(exc.detail, str) else exc.detail.dict()
#     headers = exc.headers if hasattr(exc, 'headers') else None

#     return await http_exception_handler(request,
#                                         HTTPException(
#                                             status_code=exc.status_code,
#                                             detail=detail,
#                                             headers=headers))


#@app.get("/favicon.ico", include_in_schema=False)
#async def favicon():
#    return FileResponse(config.API_FAVICON)

async def block_disabled_puzzles(request: Request, db: Annotated["Session", Depends(get_db)]):
    puzzle_name = Path(request.url.path).name
    puzzle = db.query(Puzzle).filter(Puzzle.name == puzzle_name).first()
    if puzzle is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unknown Puzzle")
    if not puzzle.active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Disabled Puzzle")


# Mount the static folder to serve common assets
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routes
app.include_router(game_router, prefix='')
app.include_router(admin_router, prefix='/admin')
app.include_router(puzzle_router, prefix='/puzzles', dependencies=[Depends(block_disabled_puzzles)])
