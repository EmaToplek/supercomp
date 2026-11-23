import io
import zipfile
from datetime import date, datetime, timedelta, timezone

import pytest
from sqlalchemy import func, select

from app import garmin_sync
from app.garmin_client import GarminError, extract_fit_from_zip
from app.garmin_sync import sync_garmin
from app.models import Activity

BASE_TIME = datetime(2026, 11, 1, 8, 0, tzinfo=timezone.utc)
BROKEN_ID = 999


class FakeGarmin:
    """Stands in for GarminClient. Each id becomes an activity starting `id` hours after BASE_TIME."""

    def __init__(self, garmin_ids):
        self.garmin_ids = garmin_ids
        self.downloaded_ids = []

    def activities_since(self, since_date):
        return [{"activityId": garmin_id} for garmin_id in self.garmin_ids]

    def download_fit(self, garmin_activity_id):
        self.downloaded_ids.append(garmin_activity_id)
        if garmin_activity_id == BROKEN_ID:
            raise GarminError("404")
        return str(garmin_activity_id).encode()  


def fake_build_activity(fit_file, athlete_settings):
    hours_after_base = int(fit_file.read())
    return Activity(
        start_time=BASE_TIME + timedelta(hours=hours_after_base),
        duration_s=1800,
        avg_hr=140,
        max_hr=170,
    )


@pytest.fixture(autouse=True)
def no_real_fit_parsing(monkeypatch):
    monkeypatch.setattr(garmin_sync, "build_activity", fake_build_activity)


@pytest.fixture
def db(test_session):
    session = test_session()
    yield session
    session.close()


def count_activities(db):
    return db.scalar(select(func.count()).select_from(Activity))


def test_saves_new_activities(db):
    result = sync_garmin(db, FakeGarmin([1, 2]), today=date(2026, 11, 5))
    assert result.new_activities == 2
    assert count_activities(db) == 2


def test_second_sync_downloads_nothing(db):
    sync_garmin(db, FakeGarmin([1, 2]))

    garmin = FakeGarmin([1, 2])
    result = sync_garmin(db, garmin)

    assert result.already_synced == 2
    assert garmin.downloaded_ids == []
    assert count_activities(db) == 2


def test_matches_activity_uploaded_by_hand(db):
    db.add(Activity(start_time=BASE_TIME + timedelta(hours=1), duration_s=1800, avg_hr=140, max_hr=170))
    db.commit()

    result = sync_garmin(db, FakeGarmin([1]))

    assert result.matched_manual_uploads == 1
    assert count_activities(db) == 1
    assert db.scalar(select(Activity.garmin_activity_id)) == 1


def test_one_failed_download_does_not_stop_the_rest(db):
    result = sync_garmin(db, FakeGarmin([BROKEN_ID, 1]))
    assert result.failed_garmin_ids == [BROKEN_ID]
    assert result.new_activities == 1


def test_extract_fit_from_zip():
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        zip_file.writestr("123_ACTIVITY.fit", b"fit-bytes")
    assert extract_fit_from_zip(zip_buffer.getvalue()) == b"fit-bytes"


def test_extract_fit_from_zip_without_fit():
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        zip_file.writestr("notes.txt", b"x")
    with pytest.raises(GarminError):
        extract_fit_from_zip(zip_buffer.getvalue())


def test_sync_returns_503_without_garmin_key(client, monkeypatch):
    monkeypatch.delenv("GARMIN_PERSONAL_KEY", raising=False)
    assert client.post("/sync").status_code == 503