from pathlib import Path
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates

from openday_scavenger.api.puzzles.dependencies import get_puzzle_name
from openday_scavenger.api.visitors.dependencies import get_auth_visitor
from openday_scavenger.api.visitors.schemas import VisitorAuth

router = APIRouter()

templates = Jinja2Templates(directory=Path(__file__).resolve().parent / "templates")

INITIAL_PARAMS: dict[str, Any] = {
    "labelthemap": {
        "map": "static/map.svg",
        "labels": [
            {
                "class": "label-accelerator",
                "style": "bottom: 94%; left: 29%;",
                "data-id": "1",
                "text": "Booster Ring",
            },
            {
                "class": "label-operational",
                "style": "bottom: 92%; right: 72%;",
                "data-id": "2",
                "text": "SAXS/WAXS",
            },
            {
                "class": "label-operational",
                "style": "bottom: 85%; left: 29%;",
                "data-id": "3",
                "text": "THz/Far-IR",
            },
            {
                "class": "label-bright",
                "style": "bottom: 1%; left: 54%;",
                "data-id": "4",
                "text": "NANO",
            },
            {
                "class": "label-bright",
                "style": "bottom: 18%; right: 10%;",
                "data-id": "5",
                "text": "MX3",
            },
            {
                "class": "label-bright",
                "style": "bottom: 9%; right: 6%;",
                "data-id": "6",
                "text": "ADS",
            },
            {
                "class": "label-accelerator",
                "style": "bottom: 1%; right: 3%;",
                "data-id": "7",
                "text": "LINAC",
            },
            {
                "class": "label-bright",
                "style": "bottom: 82%; right: 0%;",
                "data-id": "8",
                "text": "MEX1&2",
            },
            {
                "class": "label-operational",
                "style": "bottom: 91%; right: 0%;",
                "data-id": "9",
                "text": "MX1&2",
            },
            {
                "class": "label-operational",
                "style": "bottom: 94%; right: 24%",
                "data-id": "10",
                "text": "PD",
            },
            {
                "class": "label-bright",
                "style": "bottom: 83%; right: 72%",
                "data-id": "11",
                "text": "MCT",
            },
            {
                "class": "label-accelerator",
                "style": "bottom: 74.5%; right: 64%",
                "data-id": "12",
                "text": "Storage Ring",
            },
            {
                "class": "label-bright",
                "style": "bottom: 65%; right: 69%;",
                "data-id": "13",
                "text": "BioSAXS",
            },
            {
                "class": "label-operational",
                "style": "bottom: 56%; right: 71%;",
                "data-id": "14",
                "text": "XFM",
            },
            {
                "class": "label-operational",
                "style": "bottom: 35%; right: 69%;",
                "data-id": "15",
                "text": "IR",
            },
            {
                "class": "label-operational",
                "style": "bottom: 22%; right: 61%;",
                "data-id": "16",
                "text": "SXR",
            },
            {
                "class": "label-operational",
                "style": "bottom: 11%; right: 50%;",
                "data-id": "17",
                "text": "XAS",
            },
            {
                "class": "label-operational",
                "style": "bottom: 1%; left: 9%;",
                "data-id": "18",
                "text": "IMBL",
            },
        ],
    },
    "labelthemap-easy": {
        "map": "static/map-easy.svg",
        "labels": [
            {
                "class": "label-bright",
                "style": "bottom: 94%; left: 29%;",
                "data-id": "1",
                "text": "Bright Beamlines",
            },
            {
                "class": "label-operational",
                "style": "bottom: 92%; right: 72%;",
                "data-id": "2",
                "text": "Existing Beamlines",
            },
            {
                "class": "label-accelerator",
                "style": "bottom: 85%; left: 29%;",
                "data-id": "3",
                "text": "LINAC",
            },
            {
                "class": "label-accelerator",
                "style": "bottom: 10%; left: 15%",
                "data-id": "4",
                "text": "Storage Ring",
            },
            {
                "class": "label-accelerator",
                "style": "bottom: 1%; left: 15%",
                "data-id": "5",
                "text": "Booster Ring",
            },
        ],
    },
}


@router.get("/static/{path:path}")
async def get_static_files(
    path: Path,
):
    """get_static_files Serve files from a local static folder"""
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


@router.get("/")
async def index(
    request: Request,
    visitor: Annotated[VisitorAuth, Depends(get_auth_visitor)],
    puzzle_name: Annotated[str, Depends(get_puzzle_name)],
):
    initial_params = INITIAL_PARAMS.get(puzzle_name, INITIAL_PARAMS["labelthemap"])

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "puzzle": puzzle_name,
            "visitor": visitor.uid,
            "map": initial_params["map"],
            "labels_data": initial_params["labels"],
        },
    )
