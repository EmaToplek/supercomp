"""Tests for the athlete settings endpoints (GET and PUT /settings)"""

def test_get_returns_defaults(client):
    response = client.get("/settings")
    assert response.status_code == 200
    assert response.json() == {"sex": "female", "resting_hr": 65, "max_hr": 195}


def test_put_updates_settings(client):
    new = {"sex": "male", "resting_hr": 55, "max_hr": 185}
    assert client.put("/settings", json=new).status_code == 200
    assert client.get("/settings").json() == new


def test_resting_not_below_max_is_rejected(client):
    bad = {"sex": "female", "resting_hr": 120, "max_hr": 120}
    assert client.put("/settings", json=bad).status_code == 422


def test_invalid_sex_is_rejected(client):
    bad = {"sex": "other", "resting_hr": 60, "max_hr": 190}
    assert client.put("/settings", json=bad).status_code == 422