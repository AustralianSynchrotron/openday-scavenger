from fastapi import APIRouter, Depends, Request

from openday_scavenger.api.visitors.dependencies import get_auth_visitor
from openday_scavenger.api.visitors.schemas import VisitorAuth

router = APIRouter()


@router.get("/")
async def index(request: Request, visitor: VisitorAuth | None = Depends(get_auth_visitor)):
    return {
        "question": "Which part of the synchrotron is responsible for accelerating particles to near light speed?",
        "options": ["Booster", "Beamline", "Detector", "Storage Ring"],
        "hint": "It's where particles gain most of their energy.",
        "success_message": "Correct! You've found the answer!",
        "failure_message": "Incorrect, try again!",
    }
