from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter()

templates = Jinja2Templates(directory=Path(__file__).resolve().parent / "static")


@router.get("/")
async def render_index_page(request: Request):
    """Render admin index page"""
    return templates.TemplateResponse(request=request, name="index.html")
