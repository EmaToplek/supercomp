import math

import numpy as np
import pandas as pd
import pytest

from app.metrics.trimp import banister_trimp, edwards_trimp

HR_REST = 60
HR_MAX = 160


def make_samples(heart_rates, seconds_apart=1):
    """Build a samples DataFrame with evenly spaced timestamps."""
    start = pd.Timestamp("2026-10-18 08:00:00")
    timestamps = [start + pd.Timedelta(seconds=i * seconds_apart)
                  for i in range(len(heart_rates))]
    return pd.DataFrame({"timestamp": timestamps, "heart_rate": heart_rates})


def one_minute_at(hr):
    # 61 samples 1 s apart = exactly 60 s (the last sample lasts 0 s)
    return make_samples([hr] * 61)


def test_banister_matches_hand_calculation():
    # 1 min at 50 % HRR, female: 1 * 0.5 * 0.86 * e^(1.67 * 0.5)
    expected = 1 * 0.5 * 0.86 * math.exp(1.67 * 0.5)
    result = banister_trimp(one_minute_at(110), HR_REST, HR_MAX, "female")
    assert result == pytest.approx(expected)


def test_banister_male_coefficients():
    expected = 1 * 0.5 * 0.64 * math.exp(1.92 * 0.5)
    result = banister_trimp(one_minute_at(110), HR_REST, HR_MAX, "male")
    assert result == pytest.approx(expected)


def test_banister_grows_faster_than_intensity():
    # Exponential weighting: 70 % HRR gives more than 1.4x the load of 50 %
    easy = banister_trimp(one_minute_at(110), HR_REST, HR_MAX, "female")
    hard = banister_trimp(one_minute_at(130), HR_REST, HR_MAX, "female")
    assert hard > easy * 1.4


def test_banister_hr_below_rest_adds_nothing():
    assert banister_trimp(one_minute_at(50), HR_REST, HR_MAX, "female") == 0.0


def test_banister_hr_above_max_is_capped():
    at_max = banister_trimp(one_minute_at(160), HR_REST, HR_MAX, "female")
    above = banister_trimp(one_minute_at(180), HR_REST, HR_MAX, "female")
    assert above == pytest.approx(at_max)


def test_banister_missing_hr_adds_nothing():
    samples = one_minute_at(110)
    samples["heart_rate"] = samples["heart_rate"].astype(float)
    samples.loc[0:29, "heart_rate"] = np.nan  # first 30 s without HR
    full = banister_trimp(one_minute_at(110), HR_REST, HR_MAX, "female")
    half = banister_trimp(samples, HR_REST, HR_MAX, "female")
    assert half == pytest.approx(full / 2)


def test_banister_pause_is_not_counted():
    samples = make_samples([110, 110])
    samples.loc[1, "timestamp"] += pd.Timedelta(minutes=5)
    assert banister_trimp(samples, HR_REST, HR_MAX, "female") == 0.0


def test_banister_invalid_sex_raises():
    with pytest.raises(ValueError):
        banister_trimp(one_minute_at(110), HR_REST, HR_MAX, "other")


def test_edwards_matches_hand_calculation():
    # 1 min in Z1 (weight 1) + 2 min in Z3 (weight 3) = 1 + 6 = 7
    samples = make_samples([115] * 60 + [135] * 121)
    assert edwards_trimp(samples, HR_REST, HR_MAX) == pytest.approx(7.0)

def test_empty_data_gives_zero():
    empty = pd.DataFrame({"timestamp": pd.to_datetime([]), "heart_rate": []})
    assert banister_trimp(empty, HR_REST, HR_MAX, "female") == 0.0
    assert edwards_trimp(empty, HR_REST, HR_MAX) == 0.0