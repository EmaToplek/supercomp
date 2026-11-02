"""
Athlete settings endpoints (GET and PUT /settings).

Resting HR, max HR and sex are used for HR zones and TRIMP.
The app has a single athlete, so there is only one settings row.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import AthleteSettings
from app.schemas import SettingsSchema
from app.activity_metrics import recalculate_all
from app.dependencies import block_in_demo_mode

router = APIRouter(prefix="/settings", tags=["settings"])

# Single-athlete app, so there is only one settings row
SETTINGS_ID = 1


def get_or_create_settings(db: Session) -> AthleteSettings:
    settings = db.get(AthleteSettings, SETTINGS_ID)
    if settings is None:
        settings = AthleteSettings(id=SETTINGS_ID)
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings


@router.get("", response_model=SettingsSchema)
def read_settings(db: Session = Depends(get_db)):
    return get_or_create_settings(db)


@router.put(
    "", response_model=SettingsSchema, dependencies=[Depends(block_in_demo_mode)]
)
def update_settings(new: SettingsSchema, db: Session = Depends(get_db)):
    settings = get_or_create_settings(db)
    settings.sex = new.sex
    settings.resting_hr = new.resting_hr
    settings.max_hr = new.max_hr
    recalculate_all(db, settings)
    db.commit()
    db.refresh(settings)
    return settings
