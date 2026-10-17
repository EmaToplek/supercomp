"""
Parse Garmin .FIT files into pandas DataFrames.

A FIT file is a binary sequence of messages. We use two of them:
- ``record``: the time series (one row per sample: time, heart rate, speed, distance)
- ``session``: the activity summary (sport, start time, duration, avg/max heart rate)
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import BinaryIO

import fitdecode
import pandas as pd

RECORD_COLUMNS = ["timestamp", "heart_rate", "speed", "distance"]

# Heart rate gaps up to this many consecutive samples are interpolated.
# Longer gaps (e.g. sensor lost contact) stay missing so we don't invent data.
MAX_HR_GAP_SAMPLES = 5


class FitParseError(Exception):
    """Raised when a file is not a valid FIT file or contains no usable records."""


@dataclass
class ActivitySummary:
    """Summary of one activity, taken from the FIT 'session' message."""

    sport: str | None = None
    sub_sport: str | None = None
    start_time: datetime | None = None
    duration_s: float | None = None
    distance_m: float | None = None
    avg_hr: int | None = None
    max_hr: int | None = None


@dataclass
class ParsedActivity:
    """Result of parsing a FIT file."""

    records: pd.DataFrame
    summary: ActivitySummary


def read_fit(source: str | Path | BinaryIO) -> ParsedActivity:
    """
    Read a FIT file from a path or a binary file object (e.g. an upload).

    Returns per-sample records sorted by time and the session summary.
    Missing fields are stored as NaN/None instead of raising an error,
    because not every activity has every field (strength training has no speed).
    """
    records: list[dict] = []
    summary = ActivitySummary()

    try:
        with fitdecode.FitReader(source) as fit:
            for frame in fit:
                if frame.frame_type != fitdecode.FIT_FRAME_DATA:
                    continue

                if frame.name == "record":
                    records.append(_parse_record(frame))
                elif frame.name == "session":
                    summary = _parse_session(frame)
    except fitdecode.FitError as exc:
        raise FitParseError(f"Invalid FIT file: {exc}") from exc

    df = _to_dataframe(records)
    if df.empty:
        raise FitParseError("FIT file contains no records")

    df["heart_rate"] = fill_short_hr_gaps(df["heart_rate"])
    return ParsedActivity(records=df, summary=summary)


def fill_short_hr_gaps(hr: pd.Series, max_gap: int = MAX_HR_GAP_SAMPLES) -> pd.Series:
    """
    Interpolate runs of missing heart rate values that are at most ``max_gap`` samples long.

    Gaps at the start or end of the activity and longer gaps are left as NaN.
    """
    hr = hr.astype("float64")
    missing = hr.isna()
    if not missing.any():
        return hr

    # Give every run of consecutive missing values its own id and measure its length
    run_id = (missing != missing.shift()).cumsum()
    run_length = missing.groupby(run_id).transform("sum")
    short_gap = missing & (run_length <= max_gap)

    interpolated = hr.interpolate(limit_area="inside")
    return hr.where(~short_gap, interpolated)


def _parse_record(frame: fitdecode.FitDataMessage) -> dict:
    """Extract the fields we need from one 'record' message."""
    return {
        "timestamp": frame.get_value("timestamp", fallback=None),
        "heart_rate": frame.get_value("heart_rate", fallback=None),
        # Newer devices store speed as 'enhanced_speed'
        "speed": frame.get_value("enhanced_speed",
                                 fallback=frame.get_value("speed", fallback=None)),
        "distance": frame.get_value("distance", fallback=None),
    }


def _parse_session(frame: fitdecode.FitDataMessage) -> ActivitySummary:
    """Extract the activity summary from the 'session' message."""
    return ActivitySummary(
        sport=_as_str(frame.get_value("sport", fallback=None)),
        sub_sport=_as_str(frame.get_value("sub_sport", fallback=None)),
        start_time=frame.get_value("start_time", fallback=None),
        duration_s=frame.get_value("total_timer_time", fallback=None),
        distance_m=frame.get_value("total_distance", fallback=None),
        avg_hr=frame.get_value("avg_heart_rate", fallback=None),
        max_hr=frame.get_value("max_heart_rate", fallback=None),
    )


def _to_dataframe(records: list[dict]) -> pd.DataFrame:
    """Build a clean, time-sorted DataFrame with a fixed set of columns."""
    df = pd.DataFrame(records, columns=RECORD_COLUMNS)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    for column in ("heart_rate", "speed", "distance"):
        df[column] = pd.to_numeric(df[column], errors="coerce")

    # Rows without a timestamp can't be placed in time
    df = df.dropna(subset=["timestamp"])
    df = df.sort_values("timestamp").drop_duplicates(subset="timestamp")
    return df.reset_index(drop=True)


def _as_str(value: object) -> str | None:
    """FIT enums can come back as strings or ints; normalise to str or None."""
    return None if value is None else str(value)