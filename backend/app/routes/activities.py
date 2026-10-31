"""Activity endpoints: upload a FIT file, calculate its metrics and store it with its raw samples"""

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.activity_metrics import calculate_metrics
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

    # Fall back to the records if the session message is missing a value
    timestamps = records["timestamp"]
    start_time = summary.start_time or timestamps.iloc[0]
    duration_s = (
        summary.duration_s or (timestamps.iloc[-1] - timestamps.iloc[0]).total_seconds()
    )

    activity = Activity(
        start_time=start_time,
        duration_s=duration_s,
        avg_hr=summary.avg_hr,
        max_hr=summary.max_hr,
    )

    calculate_metrics(activity, records, settings)

    activity.samples = [
        ActivitySample(
            timestamp=row["timestamp"],
            heart_rate=row["heart_rate"],
            speed=row["speed"],
            distance=row["distance"],
        )
        for row in samples_for_db(records)
    ]

    db.add(activity)
    db.commit()
    db.refresh(activity)
    return activity


@router.get("", response_model=list[ActivityOut])
def list_activities(db: Session = Depends(get_db)):
    return db.query(Activity).order_by(Activity.start_time.desc()).all()

