import pandas as pd
import pytest

from app.metrics.acwr import daily_load, acwr_rolling, acwr_ewma


def make_daily(loads, start="2026-09-01"):
    """Daily load series starting at start, one value per day."""
    index = pd.date_range(start, periods=len(loads), freq="D")
    return pd.Series(loads, index=index, dtype=float)


def test_daily_load_sums_activities_on_same_day():
    loads = pd.Series(
        [50.0, 30.0],
        index=pd.to_datetime(["2026-09-01 09:00", "2026-09-01 18:00"]),
    )
    daily = daily_load(loads)
    assert list(daily) == [80.0]


def test_daily_load_filss_rest_day_with_zero():
    loads = pd.Series(
        [50.0, 40.0], index=pd.to_datetime(["2026-09-01 09:00", "2026-09-03 09:00"])
    )
    daily = daily_load(loads)
    assert list(daily) == [50.0, 0.0, 40.0]


def test_daily_load_counts_rest_days_up_to_end():
    loads = pd.Series([50.0], index=pd.to_datetime(["2026-09-01 07:00"]))
    daily = daily_load(loads, end=pd.Timestamp("2026-09-04"))
    assert list(daily) == [50.0, 0.0, 0.0, 0.0]


def test_daily_load_empty():
    assert daily_load(pd.Series(dtype=float)).empty


@pytest.mark.parametrize("method", [acwr_rolling, acwr_ewma])
def test_constant_load_gives_acwr_of_one(method):
    result = method(make_daily([100] * 40))
    assert result["acwr"].iloc[-1] == pytest.approx(1.0)


def test_load_spike_raises_acwr():
    result = acwr_rolling(make_daily([100] * 28 + [200] * 7))
    assert result["acute"].iloc[-1] == pytest.approx(200)
    assert result["chronic"].iloc[-1] == pytest.approx(125)
    assert result["acwr"].iloc[-1] == pytest.approx(1.6)


@pytest.mark.parametrize("method", [acwr_rolling, acwr_ewma])
def test_short_history_is_insufficient(method):
    result = method(make_daily([100] * 40))
    assert (result["status"].iloc[:27] == "insufficient_data").all()
    assert result["acwr"].iloc[:27].isna().all()


@pytest.mark.parametrize("method", [acwr_rolling, acwr_ewma])
def test_status_is_ok_from_day_28(method):
    result = method(make_daily([100] * 40))
    assert result["status"].iloc[27] == "ok"
    assert result["acwr"].iloc[27] == pytest.approx(1.0)


@pytest.mark.parametrize("method", [acwr_rolling, acwr_ewma])
def test_zero_chronic_load_gives_no_ratio(method):
    result = method(make_daily([0] * 30))
    assert result["acwr"].isna().all()


def test_ewma_follows_formula():
    # lambda = 2 / (7 + 1) = 0.25 for acute, 2 / (28 + 1) for chronic
    result = acwr_ewma(make_daily([100, 0]))
    # chronic lambda is 2/29, so day 2 = 100 * 27/29
    assert result["acute"].iloc[1] == pytest.approx(75)
    assert result["chronic"].iloc[1] == pytest.approx(100 * 27 / 29)


def test_ewma_has_no_drop_when_hard_day_leaves_window():
    # One hard day (400) on day 29, then normal training again (100)
    daily = make_daily([100] * 28 + [400] + [100] * 10)
    rolling_change = acwr_rolling(daily)["acwr"].diff()
    ewma_change = acwr_ewma(daily)["acwr"].diff()

    # 7 days later the hard day is no longer in 7 day window
    day_it_leaves = 28 + 7
    assert rolling_change.iloc[day_it_leaves] < -0.3
    assert abs(ewma_change.iloc[day_it_leaves]) < 0.05
