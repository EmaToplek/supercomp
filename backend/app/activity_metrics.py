"""Metric calculation for activities, shared between routes"""

import pandas as pd

from app.metrics.trimp import banister_trimp, edwards_trimp
from app.metrics.zones import time_in_zones
from app.models import Activity, AthleteSettings


def calculate_metrics(activity: Activity, records: pd.DataFrame, settings: AthleteSettings) -> None:
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


