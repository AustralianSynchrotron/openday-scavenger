from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates

from openday_scavenger.api.visitors.dependencies import get_auth_visitor
from openday_scavenger.api.visitors.schemas import VisitorAuth

router = APIRouter()

# Set up the Jinja2 template directory
templates = Jinja2Templates(directory=Path(__file__).resolve().parent / "static")


# Serve static files from the local static folder
@router.get("/static/{path:path}")
async def get_static_files(
    path: Path,
):
    """Serve files from a local static folder"""
    parent_path = Path(__file__).resolve().parent / "static"
    file_path = parent_path / path

    if file_path.is_relative_to(parent_path) and file_path.is_file():
        return FileResponse(file_path)
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Requested file does not exist"
        )


# Render the puzzle page
@router.get("/")
async def index(
    request: Request, visitor: Annotated[VisitorAuth | None, Depends(get_auth_visitor)]
):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"puzzle": "synchrotron_question", "visitor": visitor.uid},
    )
