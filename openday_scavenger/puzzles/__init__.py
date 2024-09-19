from fastapi import APIRouter

from .demo.views import router as puzzle_demo_router
from .periodic.views import router as puzzle_periodic_router

router = APIRouter()

# Include puzzle routes. Name entered into database should match the prefix.
router.include_router(puzzle_demo_router, prefix="/demo")
router.include_router(puzzle_periodic_router, prefix="/element_general")
router.include_router(puzzle_periodic_router, prefix="/element_mex")
router.include_router(puzzle_periodic_router, prefix="/element_xas")


# Include a route to catch all invalid puzzle routes so we can throw a custom 404.
@router.get("/{path:path}/")
async def catch_all(path: str):
    pass
