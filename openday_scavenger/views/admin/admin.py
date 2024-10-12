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

    all_visitors = get_all_visitors(db)

    visitor_data = [
        {
            "uid": visitor.uid,
            "check_in_time": visitor.checked_in,
            "check_out_time": visitor.checked_out,
            "correct_answers": correct_answers,
            "attempted_puzzles": attempted_puzzles,
        }
        for visitor, correct_answers, attempted_puzzles in all_visitors
    ]

    df_visitors = pd.DataFrame(visitor_data)

    if df_visitors.empty or df_visitors["check_in_time"].isnull().all():
        plotly_visitor_data = "No user data available 😔"
    else:
        # resample the data to get a count of visitors for a given frequency
        resample_period = "15min"

        checked_in_df = (
            df_visitors.resample(resample_period, on="check_in_time")["check_in_time"]
            .count()
            .cumsum()
            .reset_index(name="checked_in")
        )

        # handle case where no visitors have checked out
        if df_visitors["check_out_time"].isnull().all():
            checked_out_df = checked_in_df.copy().rename(
                columns={"check_in_time": "check_out_time", "checked_in": "checked_out"}
            )
            checked_out_df["checked_out"] = 0
        else:
            checked_out_df = (
                df_visitors.resample(resample_period, on="check_out_time")["check_out_time"]
                .count()
                .cumsum()
                .reset_index(name="checked_out")
            )

        cumulative_df = pd.merge(
            checked_in_df,
            checked_out_df,
            left_on="check_in_time",
            right_on="check_out_time",
            how="outer",
        ).fillna(0)

        # Convert datetime columns to 12-hour format
        cumulative_df["time"] = cumulative_df.apply(
            lambda row: row["check_out_time"] if row["checked_in"] == 0 else row["check_in_time"],
            axis=1,
        )
        cumulative_df["time"] = cumulative_df["time"].dt.strftime("%I:%M %p")

        # Convert datetime columns to 12-hour format
        cumulative_df["time"] = cumulative_df.apply(
            lambda row: row["check_out_time"] if row["checked_in"] == 0 else row["check_in_time"],
            axis=1,
        )
        cumulative_df["time"] = cumulative_df["time"].dt.strftime("%I:%M %p")

        visitor_fig = px.line(
            cumulative_df,
            x="time",
            y=["checked_in", "checked_out"],
            # title="Adventurers Searching for Puzzles",
            title="Today's Puzzled Puzzlers at the Synchrotron",
            labels={"time": "Time", "value": "Running Total of Visitors", "variable": "Status"},
        )

        plotly_visitor_data = visitor_fig.to_html(full_html=False)

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "active_page": "dashboard",
            "number_active_puzzles": number_active_puzzles,
            "number_active_visitors": number_active_visitors,
            "number_responses": number_responses,
            "number_correct_responses": number_correct_responses,
            "fig": plotly_visitor_data,
        },
    )
