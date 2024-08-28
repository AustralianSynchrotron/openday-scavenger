from fastapi import APIRouter

from .demo.views import router as puzzle_demo_router


router = APIRouter()

# Include puzzle routes
router.include_router(puzzle_demo_router, prefix='/demo')
