"""Tests for demo mode, which blocks writes on the public deployment."""

import pytest


@pytest.fixture
def demo_mode(monkeypatch):
    monkeypatch.setenv("DEMO_MODE", "true")


def test_upload_is_blocked_in_demo_mode(client, demo_mode):
    response = client.post(
        "/activities/upload",
        files={"file": ("run.fit", b"fake", "application/octet-stream")},
    )
    assert response.status_code == 403


def test_settings_cannot_be_changed_in_demo_mode(client, demo_mode):
    new = {"sex": "male", "resting_hr": 55, "max_hr": 185}
    assert client.put("/settings", json=new).status_code == 403


def test_reading_and_seeding_still_work_in_demo_mode(client, demo_mode):
    assert client.get("/settings").status_code == 200
    assert client.post("/activities/seed", params={"days": 28}).status_code == 201
    assert client.get("/load").status_code == 200
