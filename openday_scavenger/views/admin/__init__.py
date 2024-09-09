from fastapi import APIRouter

from .admin import router as admin_router
from .puzzles import router as puzzle_router
from .responses import router as response_router
from .visitors import router as visitor_router

router = APIRouter()

router.include_router(admin_router, prefix="")
router.include_router(puzzle_router, prefix="/puzzles")
router.include_router(visitor_router, prefix="/visitors")
router.include_router(response_router, prefix="/responses")
