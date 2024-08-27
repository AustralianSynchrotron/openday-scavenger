from fastapi import APIRouter



router = APIRouter()


@router.get("/")
async def get_test():
    return "Test2"
