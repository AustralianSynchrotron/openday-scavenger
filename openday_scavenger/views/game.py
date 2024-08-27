from typing import Annotated

from pydantic import BaseModel
from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session

from openday_scavenger.api.db import get_db
# from openday_scavenger.api.visitors import service
from openday_scavenger.api.puzzles import service as puzzle_service

router = APIRouter()


class Answer(BaseModel):
    id: str
    answer: str


@router.post("/submission")
async def submit_answer(answer: Answer, db: Annotated["Session", Depends(get_db)]):
    
    a_puzzle = puzzle_service.PuzzleCreate(
        name=answer.answer,
        answer="Blah Blah",
        location="blah reception",
        notes="Does this work"
    )

    puzzle_service.create(db, a_puzzle)
    
    if answer.answer == "3":
        return "YAY"
    else:
        return "NOPE"
