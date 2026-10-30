import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.metrics.trimp import banister_trimp, edwards_trimp
from app.metrics.zones import time_in_zones
from app.models import Activity, ActivitySample
from app.parser.fit import FitParseError, read_fit
from app.routes.settings import get_or_create_settings
from app.schemas import ActivityOut

router = APIRouter(prefix="/activities", tags=["activities"])

SAMPLE_COLUMNS = ["timestamp", "heart_rate", "speed", "distance"]

def samples_for_db(records: pd.DataFrame) -> list[dict]:
  """Convert records to plain dicts, with NaN replaced by None (NULL in the db)"""

  cols = records[SAMPLE_COLUMNS]
  return cols.astype(object).where(cols.notna(), None).to_dict("records")


@router.post("/upload", response_model=ActivityOut, status_code=status.HTTP_201_CREATED)
def upload_activity(file: UploadFile, db: Session = Depends(get_db)):
    if not file.filename or not file.filename.lower().endswith(".fit"):
        raise HTTPException(status_code=400, detail="Only .fit files are supported")

    try:
        parsed = read_fit(file.file)
    except FitParseError as e:
        raise HTTPException(status_code=400, detail=str(e))

    records, summary = parsed.records, parsed.summary
    settings = get_or_create_settings(db)
    hr_rest, hr_max = settings.resting_hr, settings.max_hr

    # Fall back to the records if the session message is missing a value
    timestamps = records["timestamp"]
    start_time = summary.start_time or timestamps.iloc[0]
    duration_s = summary.duration_s or (timestamps.iloc[-1] - timestamps.iloc[0]).total_seconds()

    zones = time_in_zones(records, hr_rest, hr_max)

    activity = Activity(
        start_time=start_time,
        duration_s=duration_s,
        avg_hr=summary.avg_hr,
        max_hr=summary.max_hr,
        trimp_banister=banister_trimp(records, hr_rest, hr_max, settings.sex),
        trimp_edwards=edwards_trimp(records, hr_rest, hr_max),
        zone1_time=zones.get(1, 0.0),
        zone2_time=zones.get(2, 0.0),
        zone3_time=zones.get(3, 0.0),
        zone4_time=zones.get(4, 0.0),
        zone5_time=zones.get(5, 0.0)
    )
    activity.samples = [
        ActivitySample(timestamp=row["timestamp"], heart_rate=row["heart_rate"], speed=row["speed"], distance=row["distance"])
        for row in samples_for_db(records)
    ]

    db.add(activity)
    db.commit()
    db.refresh(activity)
    return activity