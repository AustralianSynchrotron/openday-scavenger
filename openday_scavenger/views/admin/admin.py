from pathlib import Path
from typing import Annotated

import pandas as pd
import plotly.express as px
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from openday_scavenger.api.db import get_db
from openday_scavenger.api.puzzles.service import count as count_puzzles
from openday_scavenger.api.puzzles.service import count_responses
from openday_scavenger.api.visitors.service import count as count_visitors
from openday_scavenger.api.visitors.service import get_all as get_all_visitors

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


@router.get("/")
async def render_index_page(
    request: Request,
    db: Annotated["Session", Depends(get_db)],
):
    """Render admin index page"""

    number_active_puzzles = count_puzzles(db, only_active=True)
    number_active_visitors = count_visitors(db, still_playing=True)
    number_responses = count_responses(db, only_correct=False)
    number_correct_responses = count_responses(db, only_correct=False)

    # TODO: refactor this code to convert db data into a dataframe
    # and add it into a service, rather than this route
    all_visitors = get_all_visitors(db)
    xval = []
    yval = []
    zval = []
    for visitor, correct_answers, attempted_puzzles in all_visitors:
        xval.append(visitor.checked_in)
        zval.append(visitor.checked_out)
        yval.append(visitor.uid)

    # TODO: don't use a for loop and add more useful structured data into the df
    # index = pd.date_range('10/7/2024', periods=24, freq='h')
    checked_in_df = pd.DataFrame({"uid": yval, "checked_in": xval})
    checked_out_df = pd.DataFrame({"uid": yval, "checked_out": zval})
    if checked_in_df.empty:
        plotly_jinja_data = "No user data available 😔"
    else:
        # TODO: this only works because check_in/out times have the same range
        # need to allow for different time periods
        resample_period = "15min"
        checked_in = checked_in_df.resample(resample_period, on="checked_in").count()
        checked_out = checked_out_df.resample(resample_period, on="checked_out").count()

        checked_in["checkin_cumsum"] = checked_in["uid"].cumsum()
        checked_out["checkout_cumsum"] = checked_out["uid"].cumsum()

        df = pd.DataFrame(
            {
                "checked_in": checked_in["checkin_cumsum"],
                "checked_out": checked_out["checkout_cumsum"],
            }
        )

        # create  a line plot with both check-in and check-out data
        fig = px.line(
            df,
            # title="Number of visitors",
            labels={"index": "Time (hour)", "value": "N. visitors (cumulative)"},
        )

        plotly_jinja_data = fig.to_html(full_html=False)

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "active_page": "dashboard",
            "number_active_puzzles": number_active_puzzles,
            "number_active_visitors": number_active_visitors,
            "number_responses": number_responses,
            "number_correct_responses": number_correct_responses,
            "fig": plotly_jinja_data,
        },
    )
