import pytest

from app.generators.synthetic import (
    NORMAL_WEEK,
    phase_for_day,
    plan_for_phase,
    session_segments,
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