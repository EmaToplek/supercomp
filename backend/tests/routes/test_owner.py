"""Tests for the API key check endpoint (GET /auth/check)."""

# Set by the auth_client fixture in conftest.py
VALID_KEY = "test-key"


def test_check_without_key_returns_401(auth_client):
    assert auth_client.get("/auth/check").status_code == 401


def test_check_with_wrong_key_returns_401(auth_client):
    response = auth_client.get("/auth/check", headers={"X-API-Key": "wrong"})
    assert response.status_code == 401


def test_check_with_correct_key_returns_200(auth_client):
    response = auth_client.get("/auth/check", headers={"X-API-Key": VALID_KEY})
    assert response.status_code == 200
    assert response.json() == {"valid": True}