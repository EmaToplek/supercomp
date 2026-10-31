"""Metric calculation shared by the upload endpoint and settings recalculation."""

import pandas as pd

from app.metrics.trimp import banister_trimp, edwards_trimp
from app.metrics.zones import time_in_zones
from app.models import Activity, AthleteSettings

NUMERIC_COLUMNS = ["heart_rate", "speed", "distance"]


def calculate_metrics(
    activity: Activity, records: pd.DataFrame, settings: AthleteSettings
) -> None:
    """Fill in zone times and both TRIMP values from the samples and athlete settings."""

    hr_rest, hr_max = settings.resting_hr, settings.max_hr
    zones = time_in_zones(records, hr_rest, hr_max)

    activity.trimp_banister = banister_trimp(records, hr_rest, hr_max, settings.sex)
    activity.trimp_edwards = edwards_trimp(records, hr_rest, hr_max)
    activity.zone1_time = zones.get(1, 0.0)
    activity.zone2_time = zones.get(2, 0.0)
    activity.zone3_time = zones.get(3, 0.0)
    activity.zone4_time = zones.get(4, 0.0)
    activity.zone5_time = zones.get(5, 0.0)


def samples_to_records(samples: list) -> pd.DataFrame:
    """Rebuild the records DataFrame from stored samples (NULL becomes NaN again)."""

    records = pd.DataFrame(
        {
            "timestamp": [s.timestamp for s in samples],
            "heart_rate": [s.heart_rate for s in samples],
            "speed": [s.speed for s in samples],
            "distance": [s.distance for s in samples],
        }
    )

    records["timestamp"] = pd.to_datetime(records["timestamp"], utc=True)
    records[NUMERIC_COLUMNS] = records[NUMERIC_COLUMNS].astype(float)
    return records.sort_values("timestamp").reset_index(drop=True)


def recalculate_all(db, settings: AthleteSettings) -> int:
    """Recalculate metrics for every stored activity. Returns how many were updated."""
    activities = db.query(Activity).all()
    for activity in activities:
        records = samples_to_records(activity.samples)
        calculate_metrics(activity, records, settings)
    return len(activities)
