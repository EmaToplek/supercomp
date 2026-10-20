import pytest
import pandas as pd

from datetime import date

from app.generators.synthetic import (
    NORMAL_WEEK,
    phase_for_day,
    plan_for_phase,
    session_segments,
    simulate_session,
    generate_activities
)

# Training plan and session structure

def test_phases_in_order():
    phases = [phase_for_day(day)[0] for day in (0, 20, 38, 45, 55)]
    assert phases == ["base", "build", "overload", "detraining", "return"]


def test_build_phase_increases_volume():
    _, start = phase_for_day(14)
    _, end = phase_for_day(34)
    assert start == 1.0
    assert end > start


def test_detraining_has_no_sessions():
    assert plan_for_phase("detraining") == {}


def test_base_and_build_use_normal_week():
    assert plan_for_phase("base") == NORMAL_WEEK
    assert plan_for_phase("build") == NORMAL_WEEK


def test_normal_week_includes_rest_days():
    assert len(NORMAL_WEEK) < 7


def test_easy_session_duration():
    # 10 min warm-up + 30 min main + 5 min cool-down = 45 min
    total = sum(seconds for seconds, _ in session_segments("easy", 1.0))
    assert total == 45 * 60


def test_factor_only_changes_main_part():
    normal = session_segments("long", 1.0)
    longer = session_segments("long", 1.5)
    assert normal[0] == longer[0]       
    assert longer[1][0] == normal[1][0] * 1.5


def test_intervals_have_at_least_three_reps():
    segments = session_segments("intervals", 0.1)
    work = [s for s in segments if s[1] == 0.88]
    assert len(work) == 3


def test_unknown_session_kind_raises():
    with pytest.raises(ValueError):
        session_segments("swimming", 1.0)

# simulated activities

START = pd.Timestamp("2026-08-20 07:00")

def test_one_row_per_second():
    samples = simulate_session(START, [(3, 0.5)], hr_rest = 65, hr_max = 195)
    assert len(samples) == 3
    assert list(samples.columns) == ["timestamp", "heart_rate", "speed", "distance"]


def test_heart_rate_follows_segments():
    samples = simulate_session(START, [(2, 0.5), (2, 1.0)], hr_rest = 65, hr_max = 195)
    assert samples["heart_rate"].tolist() == [130, 130, 195, 195]


def test_distance_adds_up_speed():
    samples = simulate_session(START, [(3, 0.5)], hr_rest = 65, hr_max = 195)
    assert samples["distance"].tolist() == pytest.approx([2.4, 4.8, 7.2])


def test_timestamps_one_second_apart():
    samples = simulate_session(START, [(3, 0.5)], hr_rest = 65, hr_max = 195)
    gaps = samples["timestamp"].diff().dropna()
    assert (gaps == pd.Timedelta(seconds = 1)).all()


def test_all_session_types_present():
    kinds = {a.kind for a in generate_activities()}
    assert kinds == {"easy", "intervals", "long"}


def test_every_run_starts_at_seven():
    for activity in generate_activities():
        assert activity.start.hour == 7


def test_no_runs_during_break():
    for activity in generate_activities():
        assert not date(2026, 10, 1) <= activity.start.date() <= date(2026, 10, 10)


def test_overload_week_has_more_runs():
    activities = generate_activities()
    base = [a for a in activities if a.start.date() <= date(2026, 8, 26)]
    overload = [
        a for a in activities
        if date(2026, 9, 24) <= a.start.date() <= date(2026, 9, 30)
    ]
    assert len(overload) > len(base)

