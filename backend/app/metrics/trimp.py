"""Training impulse (TRIMP): training load of a single activity from heart rate."""

from typing import Literal

import numpy as np
import pandas as pd

from app.metrics.sampling import sample_durations
from app.metrics.zones import hrr_fraction, time_in_zones

Sex = Literal["female", "male"]

# Banister weighting coefficients (a, b): weight = a * e^(b * HRr).
# They model the exponential rise of blood lactate with intensity,
# which differs between women and men.
BANISTER_COEFFICIENTS: dict[str, tuple[float, float]] = {
    "female": (0.86, 1.67),
    "male": (0.64, 1.92),
}


def banister_trimp( samples: pd.DataFrame, hr_rest: float, hr_max: float, sex: Sex) -> float:
    """
    Banister TRIMP, summed sample by sample.

    TRIMP = sum( duration_min * HRr * a * e^(b * HRr) )
    where HRr is the heart rate reserve fraction (0 = rest, 1 = max).

    Expects columns 'timestamp' (datetime) and 'heart_rate'.
    """
    if sex not in BANISTER_COEFFICIENTS:
        raise ValueError(f"sex must be one of {list(BANISTER_COEFFICIENTS)}")
    if samples.empty:
        return 0.0

    a, b = BANISTER_COEFFICIENTS[sex]
    minutes = sample_durations(samples["timestamp"]) / 60

    # Clip to 0–1: HR below rest adds no load, and HR above the configured max is capped so a too-low max HR setting can't explode the exponent
    hrr = hrr_fraction(samples["heart_rate"], hr_rest, hr_max).clip(0, 1)

    load = minutes * hrr * a * np.exp(b * hrr)
    # Samples with missing HR give NaN; sum() skips NaN, so they add 0
    return float(load.sum())


def edwards_trimp(samples: pd.DataFrame, hr_rest: float, hr_max: float) -> float:
    """
    Edwards TRIMP: minutes in each zone multiplied by the zone number (1–5).

    Note: Edwards originally used %HRmax zones; here the same %HRR zones as
    the rest of the app are used for consistency.
    """
    seconds_per_zone = time_in_zones(samples, hr_rest, hr_max)
    total = 0.0
    for zone, seconds in seconds_per_zone.items():
        minutes = seconds / 60
        # Zone number is the weight: 1 min in Z4 counts as 4
        total += zone * minutes

    return total