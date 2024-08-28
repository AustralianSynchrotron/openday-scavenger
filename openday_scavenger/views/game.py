from typing import Annotated

from pydantic import BaseModel
from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session

from openday_scavenger.api.db import get_db
from openday_scavenger.api.puzzles.service import compare_answer
from openday_scavenger.api.puzzles.schemas import PuzzleCompare

router = APIRouter()



@router.post("/submission")
async def submit_answer(puzzle_in: PuzzleCompare, db: Annotated["Session", Depends(get_db)]):

    if compare_answer(db, puzzle_in):
        return {"success": True}
    else:
        return {"success": False}
