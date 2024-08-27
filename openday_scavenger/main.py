from fastapi import FastAPI

from openday_scavenger.admin.views import router as admin_router


app = FastAPI(
    title='Open Day Scavenger Hunt',
    description='blablabla',
    openapi_url=''
)


app.include_router(admin_router, prefix='/admin')
