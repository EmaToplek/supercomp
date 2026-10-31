"""Training load endpoint: daily load and ACWR over time"""

from datetime import date
from typing import Literal

import pandas as pd
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.metrics.acwr import acwr_ewma, acwr_rolling, daily_load
from app.models import Activity
from app.schemas import LoadPoint

router = APIRouter(prefix="/load", tags=["load"])

ACWR_METHODS = {"rolling": acwr_rolling, "ewma": acwr_ewma}


@router.get("", response_model=list[LoadPoint])
def get_load(
    trimp: Literal["banister", "edwards"] = "banister",
    method: Literal["rolling", "ewma"] = "ewma",
    end: date | None = None,
    db: Session = Depends(get_db),
):
    column = Activity.trimp_banister if trimp == "banister" else Activity.trimp_edwards
    rows = db.query(Activity.start_time, column).all()
    if not rows:
        return []

    starts, loads = zip(*rows)
    activity_loads = pd.Series(loads, index=pd.to_datetime(starts, utc=True), dtype=float)
    activity_loads = activity_loads.fillna(0.0)

    # Fill rest days up to today, so ACWR also shows what a break does
    end_day = pd.Timestamp(end or date.today(), tz="UTC")
    daily = daily_load(activity_loads, end=end_day)

    table = ACWR_METHODS[method](daily)
    table["load"] = daily
    table = table.reset_index(names="day")
    table["day"] = table["day"].dt.date
    return table.astype(object).where(table.notna(), None).to_dict("records")