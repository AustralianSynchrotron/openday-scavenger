from fastapi import APIRouter

from .schemas import Answer


router = APIRouter()


@router.post("/submission")
async def submit_answer(answer: Answer):
    if answer.answer == "3":
        return "YAY"
    else:
        return "NOPE"
