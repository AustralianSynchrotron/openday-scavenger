from fastapi import APIRouter

from .cube.views import router as puzzle_cube_router
from .demo.views import router as puzzle_demo_router
from .newbuildings.views import router as new_buildings_router
from .element.views import router as puzzle_element_router
from .shuffleanagram.views import router as puzzle_shuffleanagram_router

router = APIRouter()

# Include puzzle routes. Name entered into database should match the prefix.
router.include_router(puzzle_cube_router, prefix="/cube")
router.include_router(puzzle_demo_router, prefix="/demo")
router.include_router(puzzle_element_router, prefix="/element_general")
router.include_router(puzzle_element_router, prefix="/element_mex")
router.include_router(puzzle_element_router, prefix="/element_xas")
router.include_router(puzzle_element_router, prefix="/element_ads")
router.include_router(puzzle_element_router, prefix="/element_bsx")
router.include_router(puzzle_element_router, prefix="/element_mct")
router.include_router(puzzle_element_router, prefix="/element_mx")
router.include_router(puzzle_element_router, prefix="/element_pd")
router.include_router(new_buildings_router, prefix="/newbuildings")
router.include_router(puzzle_shuffleanagram_router, prefix="/shuffleanagram-probations")
router.include_router(puzzle_shuffleanagram_router, prefix="/shuffleanagram-crumpets")
router.include_router(puzzle_shuffleanagram_router, prefix="/shuffleanagram-toerags")
router.include_router(puzzle_shuffleanagram_router, prefix="/shuffleanagram-reboots")

# Include a route to catch all invalid puzzle routes so we can throw a custom 404.
@router.get("/{path:path}/")
async def catch_all(path: str):
    pass
