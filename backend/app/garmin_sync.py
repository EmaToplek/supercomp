"""Pulls new activities from Garmin Connect and saves them like an upload."""
import io
from dataclasses import dataclass, field
from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.activity_import import build_activity
from app.garmin_client import GarminError
from app.models import Activity
from app.parser.fit import FitParseError
from app.routes.settings import get_or_create_settings

SYNC_WINDOW_DAYS = 14


@dataclass
class SyncResult:
    new_activities: int = 0
    matched_manual_uploads: int = 0 
    already_synced: int = 0  
    failed_garmin_ids: list[int] = field(default_factory=list)


def sync_garmin(db: Session, garmin_client, today: date | None = None) -> SyncResult:
    today = today or date.today()
    result = SyncResult()

    synced_garmin_ids = set(
        db.scalars(select(Activity.garmin_activity_id).where(Activity.garmin_activity_id.is_not(None)))
    )
    athlete_settings = get_or_create_settings(db)

    for garmin_activity in garmin_client.activities_since(today - timedelta(days=SYNC_WINDOW_DAYS)):
        garmin_activity_id = garmin_activity["activityId"]
        if garmin_activity_id in synced_garmin_ids:
            result.already_synced += 1
            continue

        try:
            fit_bytes = garmin_client.download_fit(garmin_activity_id)
            new_activity = build_activity(io.BytesIO(fit_bytes), athlete_settings)
        except (GarminError, FitParseError): # e.g. manual entry without a file - try again on the next sync
            result.failed_garmin_ids.append(garmin_activity_id)
            continue
        
        manual_upload = db.scalar(select(Activity).where(Activity.start_time == new_activity.start_time))
        if manual_upload:
            manual_upload.garmin_activity_id = garmin_activity_id
            result.matched_manual_uploads += 1
        else:
            new_activity.garmin_activity_id = garmin_activity_id
            db.add(new_activity)
            result.new_activities += 1

        db.commit()

    return result