from fastapi import APIRouter

from .ant.views import router as ant_puzzle
from .ads_question_answer_matchup.views import router as ads_question_answer_matchup_router
from .cube.views import router as puzzle_cube_router
from .demo.views import router as puzzle_demo_router
from .element.views import router as puzzle_element_router
from .finder.views import puzzle_routes as puzzle_finder_routes
from .finder.views import router as puzzle_finder_router
from .fourbyfour.views import router as puzzle_fourbyfour_router
from .newbuildings.views import router as new_buildings_router
from .shuffleanagram.views import router as puzzle_shuffleanagram_router
from .xray_filters.views import router as puzzle_xray_filters_router

router = APIRouter()

# Include puzzle routes. Name entered into database should match the prefix.
router.include_router(puzzle_cube_router, prefix="/cube")
router.include_router(puzzle_demo_router, prefix="/demo")
for rr in puzzle_finder_routes:
    router.include_router(puzzle_finder_router, prefix=rr)
router.include_router(puzzle_element_router, prefix="/element_general")
router.include_router(puzzle_element_router, prefix="/element_mex")
router.include_router(puzzle_element_router, prefix="/element_xas")
router.include_router(puzzle_element_router, prefix="/element_ads")
router.include_router(puzzle_element_router, prefix="/element_bsx")
router.include_router(puzzle_element_router, prefix="/element_mct")
router.include_router(puzzle_element_router, prefix="/element_mx")
router.include_router(puzzle_element_router, prefix="/element_pd")
router.include_router(new_buildings_router, prefix="/newbuildings")
router.include_router(ant_puzzle, prefix="/ant")
router.include_router(puzzle_shuffleanagram_router, prefix="/shuffleanagram-probations")
router.include_router(puzzle_shuffleanagram_router, prefix="/shuffleanagram-crumpets")
router.include_router(puzzle_shuffleanagram_router, prefix="/shuffleanagram-toerags")
router.include_router(puzzle_shuffleanagram_router, prefix="/shuffleanagram-reboots")
router.include_router(ads_question_answer_matchup_router, prefix="/ads_question_answer_matchup")
router.include_router(puzzle_fourbyfour_router, prefix="/fourbyfour")
router.include_router(puzzle_xray_filters_router, prefix="/xray_filters")


# Include a route to catch all invalid puzzle routes so we can throw a custom 404.
@router.get("/{path:path}/")
async def catch_all(path: str):
    pass
