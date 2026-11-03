"""Tests for the API key check on endpoints that change data."""

VALID_SETTINGS = {"sex": "female", "resting_hr": 65, "max_hr": 195}


def test_missing_key_returns_401(auth_client):
    response = auth_client.put("/settings", json=VALID_SETTINGS)
    assert response.status_code == 401


def test_wrong_key_returns_401(auth_client):
    response = auth_client.put(
        "/settings", json=VALID_SETTINGS, headers={"X-API-Key": "wrong"}
    )
    assert response.status_code == 401


def test_correct_key_is_accepted(auth_client):
    response = auth_client.put(
        "/settings", json=VALID_SETTINGS, headers={"X-API-Key": "test-key"}
    )
    assert response.status_code == 200


def test_missing_server_key_returns_503(auth_client, monkeypatch):
    monkeypatch.delenv("API_KEY")
    response = auth_client.put(
        "/settings", json=VALID_SETTINGS, headers={"X-API-Key": "test-key"}
    )
    assert response.status_code == 503


def test_read_endpoints_stay_public(auth_client):
    assert auth_client.get("/activities").status_code == 200
    assert auth_client.get("/settings").status_code == 200
