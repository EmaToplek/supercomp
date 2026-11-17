"""Turns a FIT file into an Activity with metrics and samples. Used by upload, seed and Garmin sync."""
from typing import BinaryIO

import pandas as pd

from app.activity_metrics import calculate_metrics
from app.models import Activity, ActivitySample
from app.parser.fit import read_fit

SAMPLE_COLUMNS = ["timestamp", "heart_rate", "speed", "distance"]


def samples_for_db(records: pd.DataFrame) -> list[dict]:
    """Converts records to plain dicts, with NaN replaced by None (NULL in the db)."""
    cols = records[SAMPLE_COLUMNS]
    return cols.astype(object).where(cols.notna(), None).to_dict("records")


def make_samples(records: pd.DataFrame) -> list[ActivitySample]:
    """Converts the FIT records into ActivitySample rows for the db."""
    return [
        ActivitySample(
            timestamp=row["timestamp"],
            heart_rate=row["heart_rate"],
            speed=row["speed"],
            distance=row["distance"],
        )
        for row in samples_for_db(records)
    ]


def build_activity(fit_file: BinaryIO, settings) -> Activity:
    """Parses the file and calculates metrics. Raises FitParseError. Does not touch the db."""
    parsed = read_fit(fit_file)
    records, summary = parsed.records, parsed.summary

    # Fall back to the records if the session message is missing a value
    timestamps = records["timestamp"]
    start_time = summary.start_time or timestamps.iloc[0]
    duration_s = summary.duration_s or (timestamps.iloc[-1] - timestamps.iloc[0]).total_seconds()

    activity = Activity(
        start_time=start_time,
        duration_s=duration_s,
        avg_hr=summary.avg_hr,
        max_hr=summary.max_hr,
    )
    calculate_metrics(activity, records, settings)
    activity.samples = make_samples(records)
    return activity