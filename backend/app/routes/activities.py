"""Activity endpoints: upload a FIT file, list activities and show one with its raw samples."""

from datetime import date, timedelta
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, UploadFile, status, Query
from sqlalchemy.orm import Session
from app.auth import require_api_key

from app.database import get_db
from app.activity_metrics import calculate_metrics
from app.models import Activity, ActivitySample
from app.parser.fit import FitParseError
from app.routes.settings import get_or_create_settings
from app.schemas import ActivityOut, ActivityDetail, SeedResult
from app.generators.synthetic import generate_activities
from app.activity_import import build_activity, make_samples

router = APIRouter(prefix="/activities", tags=["activities"])

SAMPLE_COLUMNS = ["timestamp", "heart_rate", "speed", "distance"]


def samples_for_db(records: pd.DataFrame) -> list[dict]:
    """Convert records to plain dicts, with NaN replaced by None (NULL in the db)"""

    cols = records[SAMPLE_COLUMNS]
    return cols.astype(object).where(cols.notna(), None).to_dict("records")


@router.post(
    "/upload",
    response_model=ActivityOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_api_key)],
)
def upload_activity(file: UploadFile, db: Session = Depends(get_db)):
    if not file.filename or not file.filename.lower().endswith(".fit"):
        raise HTTPException(status_code=400, detail="Only .fit files are supported")

    settings = get_or_create_settings(db)
    try:
        activity = build_activity(file.file, settings)
    except FitParseError as e:
        raise HTTPException(status_code=400, detail=str(e))

    db.add(activity)
    db.commit()
    db.refresh(activity)
    return activity


@router.get("", response_model=list[ActivityOut])
def list_activities(db: Session = Depends(get_db)):
    return db.query(Activity).order_by(Activity.start_time.desc()).all()


@router.get("/{activity_id}", response_model=ActivityDetail)
def get_activity(activity_id: int, db: Session = Depends(get_db)):
    activity = db.get(Activity, activity_id)
    if activity is None:
        raise HTTPException(status_code=404, detail="Activity not found")
    return activity


@router.post(
    "/seed",
    response_model=SeedResult,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_api_key)],
)
def seed_demo_data(days: int = Query(60, ge=28, le=365), db: Session = Depends(get_db)):
    """Fill an empty database with synthetic training, so the dashboard has data to show."""
    if db.query(Activity).first() is not None:
        raise HTTPException(
            status_code=409, detail="Database already contains activities"
        )

    settings = get_or_create_settings(db)
    generated = generate_activities(
        start_date=date.today() - timedelta(days=days),
        days=days,
        hr_rest=settings.resting_hr,
        hr_max=settings.max_hr,
    )

    for synthetic in generated:
        # The generator works with naive times; the db stores UTC
        records = synthetic.samples.copy()
        records["timestamp"] = records["timestamp"].dt.tz_localize("UTC")
        timestamps, hr = records["timestamp"], records["heart_rate"]

        activity = Activity(
            start_time=synthetic.start.tz_localize("UTC"),
            duration_s=(timestamps.iloc[-1] - timestamps.iloc[0]).total_seconds(),
            avg_hr=int(round(hr.mean())),
            max_hr=int(round(hr.max())),
        )
        calculate_metrics(activity, records, settings)
        activity.samples = make_samples(records)
        db.add(activity)

    db.commit()
    return {"created": len(generated)}
