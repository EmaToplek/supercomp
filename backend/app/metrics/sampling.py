"""Helpers for working with irregularly spaced activity samples."""

import pandas as pd

# Gaps between samples longer than this are treated as pauses
# (e.g. auto-pause at a traffic light) and are not counted.
MAX_SAMPLE_GAP_S = 10


def sample_durations(timestamps: pd.Series) -> pd.Series:
    """Seconds each sample 'lasts' = time until the next sample.

    Works for Garmin smart recording (irregular intervals).
    Gaps longer than MAX_SAMPLE_GAP_S and the last sample get 0.
    """
    duration = timestamps.diff().shift(-1).dt.total_seconds()
    # NaN (last sample) also fails the condition, so it becomes 0
    return duration.where(duration <= MAX_SAMPLE_GAP_S, 0.0)