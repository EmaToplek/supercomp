"""Heart rate zones based on heart rate reserve (Karvonen method)."""

import numpy as np
import pandas as pd

# Zone boundaries as a fraction of heart rate reserve (HRR)
# Below 0.5 = zone 0 (not counted), 0.5–0.6 = Z1, ..., >= 0.9 = Z5
ZONE_EDGES = [-np.inf, 0.5, 0.6, 0.7, 0.8, 0.9, np.inf]
ZONE_LABELS = [0, 1, 2, 3, 4, 5]

# Gaps between samples longer than this are treated as pauses
# (e.g. auto-pause at a traffic light) and are not counted as time in a zone
MAX_SAMPLE_GAP_S = 10


def hrr_fraction(hr: pd.Series, hr_rest: float, hr_max: float) -> pd.Series:
    """
    Express heart rate as a fraction of heart rate reserve.

    0.0 = resting HR, 1.0 = max HR. Values can fall outside 0–1.
    """
    if hr_max <= hr_rest:
        raise ValueError("hr_max must be greater than hr_rest")
    return (hr - hr_rest) / (hr_max - hr_rest)

def zone_for_fraction(fraction: float) -> int | None:
    """Return the zone (0–5) for a single HRR fraction, or None if HR is missing."""
    if pd.isna(fraction):
        return None  # no heart rate -> no zone
    if fraction < 0.5:
        return 0
    elif fraction < 0.6:
        return 1
    elif fraction < 0.7:
        return 2
    elif fraction < 0.8:
        return 3
    elif fraction < 0.9:
        return 4
    else:
        return 5

def assign_zones(hr: pd.Series, hr_rest: float, hr_max: float) -> pd.Series:
    """Return the zone (0–5) for every sample. Missing HR stays <NA>."""
    fraction = hrr_fraction(hr, hr_rest, hr_max)
    # Apply the scalar function to every value in the column
    zones = [zone_for_fraction(f) for f in fraction]
    return pd.Series(zones, index=hr.index, dtype="Int64")

def time_in_zones( samples: pd.DataFrame, hr_rest: float, hr_max: float) -> dict[int, float]:
    """
    Seconds spent in each zone Z1–Z5.

    Expects columns 'timestamp' (datetime) and 'heart_rate'.
    Each sample is weighted by the time until the next sample, so the
    function also works for Garmin "smart recording" (irregular intervals).
    """
    if samples.empty:
        return {zone: 0.0 for zone in range(1, 6)}

    # Duration each sample "lasts" = time until the next sample
    duration = samples["timestamp"].diff().shift(-1).dt.total_seconds()
    # Long gaps are pauses; the last sample has no successor (NaN) -> 0
    duration = duration.where(duration <= MAX_SAMPLE_GAP_S, 0.0)

    zones = assign_zones(samples["heart_rate"], hr_rest, hr_max)
    # observed=False keeps empty zones; NaN zones (missing HR) are dropped
    totals = duration.groupby(zones, observed=False).sum()

    return {zone: float(totals.get(zone, 0.0)) for zone in range(1, 6)}