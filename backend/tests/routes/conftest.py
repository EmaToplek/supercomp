"""Shared fixtures for API route tests: an in-memory SQLite database and a test client"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.auth import require_api_key


@pytest.fixture
def test_session():
    """Session factory for an in-memory SQLite db, so tests never touch Postgres"""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)


@pytest.fixture
def client(test_session):
    def override_get_db():
        db = test_session()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    # Route tests check route logic, auth has its own tests
    app.dependency_overrides[require_api_key] = lambda: None
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def auth_client(client, monkeypatch):
    """Same client, but with the real API key check."""
    monkeypatch.setenv("API_KEY", "test-key")
    app.dependency_overrides.pop(require_api_key)
    return client
