import pandas as pd

from app.metrics.acwr import daily_load

def test_daily_load_sums_activities_on_same_day(): 
    loads = pd.Series(
        [50.0, 30.0],
        index=pd.to_datetime(["2026-09-01 09:00", "2026-09-01 18:00"]),
    )
    daily = daily_load(loads)
    assert list(daily) == [80.0]

def test_daily_load_filss_rest_day_with_zero(): 
    loads = pd.Series(
        [50.0, 40.0], 
        index=pd.to_datetime(["2026-09-01 09:00", "2026-09-03 09:00"])
    )
    daily = daily_load(loads)
    assert list(daily) == [50.0, 0.0, 40.0]

def test_daily_load_counts_rest_days_up_to_end():
    loads = pd.Series([50.0], index=pd.to_datetime(["2026-09-01 07:00"]))
    daily = daily_load(loads, end=pd.Timestamp("2026-09-04"))
    assert list(daily) == [50.0, 0.0, 0.0, 0.0]


def test_daily_load_empty():
    assert daily_load(pd.Series(dtype=float)).empty

