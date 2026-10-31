"""Tests for the FIT upload endpoint. read_fit is mocked, since real FIT files are not in the repo"""

from datetime import datetime, timezone

import pandas as pd
import pytest

from app.metrics.trimp import banister_trimp, edwards_trimp
from app.models import Activity, ActivitySample
from app.parser.fit import ActivitySummary, ParsedActivity

START = datetime(2026, 10, 18, 8, 0, tzinfo=timezone.utc)


def make_records(heart_rates):
    """Records like read_fit returns them, one sample per second"""
    n = len(heart_rates)
    return pd.DataFrame(
        {
            "timestamp": pd.date_range(START, periods=n, freq="s"),
            "heart_rate": pd.Series(heart_rates, dtype=float),
            "speed": 3.0,
            "distance": [3.0 * i for i in range(n)],
        }
    )


@pytest.fixture
def fake_read_fit(monkeypatch):
    """Make the route's read_fit return a prepared activity instead of parsing a file"""

    def use(records, summary=None):
        parsed = ParsedActivity(records=records, summary=summary or ActivitySummary())
        monkeypatch.setattr("app.routes.activities.read_fit", lambda source: parsed)

    return use


def upload(client, filename="run.fit", content=b"fake"):
    return client.post(
        "/activities/upload",
        files={"file": (filename, content, "application/octet-stream")},
    )


def test_upload_returns_created_activity(client, fake_read_fit):
    records = make_records([150] * 121)
    fake_read_fit(
        records,
        ActivitySummary(start_time=START, duration_s=120, avg_hr=150, max_hr=150),
    )

    response = upload(client)

    assert response.status_code == 201
    body = response.json()
    assert body["duration_s"] == 120
    assert body["avg_hr"] == 150
    assert body["trimp_edwards"] == pytest.approx(
        edwards_trimp(records, 65, 195)
    )  # Default settings: resting 65, max 195, female


def test_metrics_use_saved_settings(client, fake_read_fit):
    client.put("/settings", json={"sex": "male", "resting_hr": 50, "max_hr": 190})
    records = make_records([150] * 121)
    fake_read_fit(records)

    body = upload(client).json()

    assert body["trimp_banister"] == pytest.approx(
        banister_trimp(records, 50, 190, "male")
    )


def test_missing_summary_falls_back_to_records(client, fake_read_fit):
    fake_read_fit(make_records([140] * 121))

    body = upload(client).json()

    assert body["start_time"].startswith("2026-10-18T08:00:00")
    assert body["duration_s"] == 120


def test_samples_are_saved_with_missing_hr_as_null(client, test_session, fake_read_fit):
    fake_read_fit(make_records([120, None, 130]))

    activity_id = upload(client).json()["id"]

    with test_session() as db:
        samples = (
            db.query(ActivitySample)
            .filter_by(activity_id=activity_id)
            .order_by(ActivitySample.timestamp)
            .all()
        )
    assert len(samples) == 3
    assert samples[0].heart_rate == 120
    assert samples[1].heart_rate is None


def test_wrong_extension_is_rejected(client):
    response = upload(client, filename="notes.txt")
    assert response.status_code == 400


def test_invalid_fit_content_is_rejected_and_nothing_saved(client, test_session):
    # Real parser here: a text file renamed to .fit
    response = upload(client, filename="fake.fit", content=b"not a fit file")

    assert response.status_code == 400
    with test_session() as db:
        assert db.query(Activity).count() == 0


def test_changing_settings_recalculates_metrics(client, test_session, fake_read_fit):
    records = make_records([150, None, 155] + [160] * 118)
    fake_read_fit(records)
    activity_id = upload(client).json()["id"]

    client.put("/settings", json={"sex": "male", "resting_hr": 50, "max_hr": 190})

    with test_session() as db:
        activity = db.get(Activity, activity_id)
        assert activity.trimp_banister == pytest.approx(
            banister_trimp(records, 50, 190, "male")
        )
        assert activity.trimp_edwards == pytest.approx(edwards_trimp(records, 50, 190))
