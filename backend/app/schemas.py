"""
Pydantic schemas: what the API accepts and returns.

They validate incoming JSON and control which fields are sent back, separately from the SQLAlchemy models in models.py.
"""

from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator
from datetime import datetime, date


class SettingsSchema(BaseModel):
    """Athlete settings used for HR zones and TRIMP."""

    model_config = ConfigDict(from_attributes=True)

    sex: Literal["female", "male"]
    resting_hr: int = Field(ge=30, le=120)
    max_hr: int = Field(ge=120, le=230)

    @model_validator(mode="after")
    def check_hr_order(self):
        if self.resting_hr >= self.max_hr:
            raise ValueError("resting_hr must be lower than max_hr")
        return self


class ActivityOut(BaseModel):
    """Activity summary returned by API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    start_time: datetime
    duration_s: float
    avg_hr: int | None
    max_hr: int | None
    trimp_banister: float | None
    trimp_edwards: float | None
    zone1_time: float
    zone2_time: float
    zone3_time: float
    zone4_time: float
    zone5_time: float


class SampleOut(BaseModel):
    """One raw sample, used for the heart rate curve."""

    model_config = ConfigDict(from_attributes=True)

    timestamp: datetime
    heart_rate: float | None
    speed: float | None
    distance: float | None


class ActivityDetail(ActivityOut):
    """Activity summary together with its raw samples."""

    samples: list[SampleOut]


class LoadPoint(BaseModel):
    """Training load and ACWR for one day."""

    day: date
    load: float
    acute: float
    chronic: float
    acwr: float | None
    status: Literal["ok", "insufficient_data"]


class SeedResult(BaseModel):
    """How many synthetic activities were created."""

    created: int

class SyncOut(BaseModel): 
    model_config = ConfigDict(from_attributes=True)

    new_activities: int
    matched_manual_uploads: int
    already_synced: int
    failed_garmin_ids: list[int]
