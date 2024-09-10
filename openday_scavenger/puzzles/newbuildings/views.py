from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import APIRouter, Depends, HTTPException,  status
from pathlib import Path
from fastapi.responses import FileResponse
from openday_scavenger.api.visitors.dependencies import get_auth_visitor
from openday_scavenger.api.visitors.schemas import VisitorAuth
from typing import Annotated

router = APIRouter()
templates = Jinja2Templates(directory=Path(__file__).resolve().parent / "templates")


@router.get("/static/{path:path}")
async def get_static_files(
    path: Path,
):
    """Serve files from a local static folder"""
    # This route is required as the current version of FastAPI doesn't allow
    # the mounting of folders on APIRouter. This is an open issue:
    # https://github.com/fastapi/fastapi/discussions/9070
    parent_path = Path(__file__).resolve().parent / "static"
    file_path = parent_path / path

    # Make sure the requested path is a file and relative to this path
    if file_path.is_relative_to(parent_path) and file_path.is_file():
        return FileResponse(file_path)
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Requested file does not exist"
        )

@router.get("/", response_class=HTMLResponse)
async def new_buildings(request: Request, visitor: Annotated[VisitorAuth | None, Depends(get_auth_visitor)]): 
    return templates.TemplateResponse(
        request=request, name="index.html",  context={"puzzle": "newbuildings", "visitor": visitor.uid}
    )

        
    

