from fastapi import APIRouter

from .demo.views import router as puzzle_demo_router
from .ant.views import router as ant_puzzle
router = APIRouter()

# Include puzzle routes. Name entered into database should match the prefix.
router.include_router(puzzle_demo_router, prefix="/demo")
router.include_router(ant_puzzle, prefix="/ant")

# Include a route to catch all invalid puzzle routes so we can throw a custom 404.
@router.get("/{path:path}/")
async def catch_all(path: str):
    pass
