from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory=Path(__file__).resolve().parent / "static")


@router.get("/")
async def render_map_page(request: Request):
    """Render the map admin page"""
    return templates.TemplateResponse(request=request, name="map.html")
