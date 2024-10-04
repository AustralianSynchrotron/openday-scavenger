from fastapi import APIRouter

from .demo.views import router as puzzle_demo_router
from .finder.views import puzzle_routes as puzzle_finder_routes
from .finder.views import router as puzzle_finder_router

router = APIRouter()

# Include puzzle routes. Name entered into database should match the prefix.
router.include_router(puzzle_demo_router, prefix="/demo")
for rr in puzzle_finder_routes:
    router.include_router(puzzle_finder_router, prefix=rr)


# Include a route to catch all invalid puzzle routes so we can throw a custom 404.
@router.get("/{path:path}/")
async def catch_all(path: str):
    pass
