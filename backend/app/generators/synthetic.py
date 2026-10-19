"""
Synthetic training data for developing and demoing ACWR.

Generates ~60 days of realistic running sessions in the same per-second format as the FIT parser (timestamp, heart_rate, speed, distance), 
with a normal base period, a build-up, one overload week and a detraining break.
"""

from dataclasses import dataclass
from datetime import date, timedelta

import numpy as np
import pandas as pd

# Heart rate does not jump to a new level instantly; it approaches it exponentially. ~30 s is a typical time constant for moderate exercise
HR_TIME_CONSTANT_S = 30

# Weekly plan for a normal week (0 = Monday). Missing days are rest days
NORMAL_WEEK = {1: "easy", 2: "intervals", 4: "easy", 5: "long"}

# Overload week: two extra sessions on top of the normal plan
OVERLOAD_WEEK = {0: "easy", 1: "easy", 2: "intervals", 3: "easy", 4: "intervals", 5: "long"}

# Returning after the break: two short, easy sessions per week
RETURN_WEEK = {1: "easy", 5: "easy"}


@dataclass
class SyntheticActivity:
    start: pd.Timestamp
    kind: str  # easy, intervals, long
    samples: pd.DataFrame  # columns: timestamp, heart_rate, speed, distance


def phase_for_day(day: int) -> tuple[str, float]:
    """Training phase and volume factor for a day index (0 = first day)."""
    if day < 14:
        return "base", 1.0
    if day < 35:
        # Build-up: volume grows gradually from 1.0 to ~1.3
        return "build", 1.0 + 0.3 * (day - 14) / 21
    if day < 42:
        return "overload", 1.6
    if day < 52:
        return "detraining", 0.0
    return "return", 0.7


def plan_for_phase(phase: str) -> dict[int, str]:
    """Which session type happens on which weekday in a given phase."""
    if phase == "overload":
        return OVERLOAD_WEEK
    if phase == "detraining":
        return {}
    if phase == "return":
        return RETURN_WEEK
    return NORMAL_WEEK


def session_segments(kind: str, factor: float) -> list[tuple[int, float]]:
    """Session structure as (duration in seconds, target fraction of HRR)."""
    if kind == "easy":
        return [(600, 0.50), (round(1800 * factor), 0.62), (300, 0.50)]
    if kind == "long":
        return [(600, 0.50), (round(3600 * factor), 0.66), (300, 0.50)]
    if kind == "intervals":
        reps = max(3, round(5 * factor))
        work_and_rest = [(180, 0.88), (120, 0.60)] * reps
        return [(900, 0.55), *work_and_rest, (600, 0.50)]
    raise ValueError(f"unknown session kind: {kind}")

