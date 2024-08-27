from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from openday_scavenger.admin.views import router as admin_router
from openday_scavenger.puzzles.demo.views import router as puzzle_demo_router
from openday_scavenger.game.views import router as game_router


app = FastAPI(
    title='Open Day Scavenger Hunt',
    description='blablabla',
    openapi_url=''
)

# Mount the static folder to serve common assets
app.mount("/static", StaticFiles(directory="static"), name="static")


# Include core routes
app.include_router(admin_router, prefix='/admin')
app.include_router(game_router, prefix='/game')

# Include puzzle routes
app.include_router(puzzle_demo_router, prefix='/puzzles/demo')




