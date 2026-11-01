"""Tests for the training load endpoint (GET /load)."""

from datetime import datetime, timedelta, timezone

import pytest

from app.models import Activity

FIRST_DAY = datetime(2026, 9, 1, 7, 0, tzinfo=timezone.utc)


def add_activities(test_session, daily_loads):
    """Store one activity per day; Edwards is set to double Banister to tell them apart."""
    with test_session() as db:
        for i, load in enumerate(daily_loads):
            db.add(
                Activity(
                    start_time=FIRST_DAY + timedelta(days=i),
                    duration_s=3600,
                    trimp_banister=load,
                    trimp_edwards=load * 2,
                )
            )
        db.commit()


def test_no_activities_gives_empty_list(client):
    assert client.get("/load").json() == []


@pytest.mark.parametrize("method", ["rolling", "ewma"])
def test_constant_load_gives_acwr_of_one(client, test_session, method):
    add_activities(test_session, [100] * 30)

    points = client.get("/load", params={"method": method, "end": "2026-09-30"}).json()

    assert len(points) == 30
    assert points[0]["status"] == "insufficient_data"
    assert points[0]["acwr"] is None
    assert points[-1]["status"] == "ok"
    assert points[-1]["acwr"] == pytest.approx(1.0)


def test_rest_days_are_filled_up_to_end(client, test_session):
    add_activities(test_session, [50])

    points = client.get("/load", params={"end": "2026-09-04"}).json()

    assert [p["day"] for p in points] == [
        "2026-09-01",
        "2026-09-02",
        "2026-09-03",
        "2026-09-04",
    ]
    assert [p["load"] for p in points] == [50, 0, 0, 0]


def test_edwards_trimp_can_be_chosen(client, test_session):
    add_activities(test_session, [50])

    point = client.get(
        "/load", params={"trimp": "edwards", "end": "2026-09-01"}
    ).json()[0]

    assert point["load"] == 100


def test_unknown_method_is_rejected(client):
    assert client.get("/load", params={"method": "magic"}).status_code == 422
