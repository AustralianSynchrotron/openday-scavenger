from typing import Annotated
from pathlib import Path
from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates

from openday_scavenger.api.visitors.schemas import VisitorAuth
from openday_scavenger.api.visitors.dependencies import get_auth_visitor


router = APIRouter()

templates = Jinja2Templates(directory=Path(__file__).resolve().parent / 'static')


@router.get('/')
async def index(request: Request, visitor: Annotated[VisitorAuth | None, Depends(get_auth_visitor)]):
    return templates.TemplateResponse(
        request=request, name='index.html',
        context={
            "puzzle_id": "demo",
            "visitor_uid": visitor.uid
        }
    )
