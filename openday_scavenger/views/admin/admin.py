from pathlib import Path
from typing import Annotated

import pandas as pd
import plotly.express as px
from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from openday_scavenger.api.db import get_db
from openday_scavenger.api.puzzles.service import count as count_puzzles
from openday_scavenger.api.puzzles.service import count_responses
from openday_scavenger.api.visitors.service import count as count_visitors
from openday_scavenger.api.visitors.service import get_all as get_all_visitors

router = APIRouter()

templates = Jinja2Templates(directory=Path(__file__).resolve().parent / "static")


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
    visitor_df = pd.DataFrame({"uid": yval, "checked_in": xval})
    checked_out_df = pd.DataFrame({"uid": yval, "checked_out": zval})
    if visitor_df.empty:
        plotly_jinja_data = "No user data available 😔"
    else:
        resample_period = "30min"
        grouped = visitor_df.resample(resample_period, on="checked_in").count()
        gr_checkout = checked_out_df.resample(resample_period, on="checked_out").count()

        grouped["checkin_cumsum"] = grouped["uid"].cumsum()
        gr_checkout["checkout_cumsum"] = gr_checkout["uid"].cumsum()

        df = pd.concat([grouped, gr_checkout])

        # create  a line plot with both check-in and check-out data
        fig = px.line(
            df,
            x=df.index,
            y="checkin_cumsum",
            title="Number of visitors",
            labels={"index": "check-in time", "checkin_cumsum": "N. visitors (cumulative)"},
            # labels={grouped.index.name: "check-in time", "": "N. visitors (cumulative)"},
        )
        fig.add_scatter(
            x=df.index,
            y=df["checkout_cumsum"],
            mode="lines",
            name="Checked-out visitors",
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
