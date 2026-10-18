import numpy as np
import pandas as pd
import pytest

from app.metrics.zones import assign_zones, time_in_zones

HR_REST = 60
HR_MAX = 160


def make_samples(heart_rates, seconds_apart=1):
    """Build a samples DataFrame with evenly spaced timestamps."""
    start = pd.Timestamp("2026-10-18 08:00:00")
    timestamps = [start + pd.Timedelta(seconds=i * seconds_apart)
                  for i in range(len(heart_rates))]
    return pd.DataFrame({"timestamp": timestamps, "heart_rate": heart_rates})


def test_zone_boundaries():
    hr = pd.Series([109, 110, 119, 120, 150, 170])
    zones = assign_zones(hr, HR_REST, HR_MAX).tolist()
    assert zones == [0, 1, 1, 2, 5, 5]


def test_missing_hr_has_no_zone():
    zones = assign_zones(pd.Series([np.nan, 130]), HR_REST, HR_MAX)
    assert pd.isna(zones.iloc[0])
    assert zones.iloc[1] == 3


def test_time_in_zones_regular_sampling():
    # 4 samples 1 s apart -> the first 3 each last 1 s, the last one 0 s
    samples = make_samples([115, 115, 135, 135])
    result = time_in_zones(samples, HR_REST, HR_MAX)
    assert result == {1: 2.0, 2: 0.0, 3: 1.0, 4: 0.0, 5: 0.0}


def test_pause_is_not_counted():
    samples = make_samples([115, 115])
    samples.loc[1, "timestamp"] += pd.Timedelta(minutes=5)  # long pause
    result = time_in_zones(samples, HR_REST, HR_MAX)
    assert result[1] == 0.0


def test_empty_dataframe():
    empty = pd.DataFrame({"timestamp": pd.to_datetime([]), "heart_rate": []})
    assert sum(time_in_zones(empty, HR_REST, HR_MAX).values()) == 0.0


def test_invalid_settings_raise():
    with pytest.raises(ValueError):
        assign_zones(pd.Series([120]), hr_rest=180, hr_max=160)