from fastapi import APIRouter

from .demo.views import router as puzzle_demo_router
from .shuffleanagram.views import router as puzzle_shuffleanagram_router

router = APIRouter()

# Include puzzle routes. Name entered into database should match the prefix.
router.include_router(puzzle_demo_router, prefix="/demo")
router.include_router(puzzle_shuffleanagram_router, prefix="/shuffleanagram-probations")
router.include_router(puzzle_shuffleanagram_router, prefix="/shuffleanagram-crumpets")
router.include_router(puzzle_shuffleanagram_router, prefix="/shuffleanagram-toerags")
router.include_router(puzzle_shuffleanagram_router, prefix="/shuffleanagram-reboots")


# Include a route to catch all invalid puzzle routes so we can throw a custom 404.
@router.get("/{path:path}/")
async def catch_all(path: str):
    pass
