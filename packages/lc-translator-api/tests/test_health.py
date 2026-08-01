"""Tests for API health endpoint."""

from __future__ import annotations

from collections.abc import Generator
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient
from sqlalchemy import StaticPool, create_engine
from sqlalchemy.orm import Session, sessionmaker

from lc_translator_api.dependencies import get_db
from lc_translator_api.main import create_app
from lc_translator_api.models.record import Base

_engine = create_engine(
    "sqlite:///:memory:",
    future=True,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
Base.metadata.create_all(bind=_engine)
_TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)


def _override_get_db() -> Generator[Session, None, None]:
    session = _TestSessionLocal()
    try:
        yield session
    finally:
        session.close()


def _broken_db() -> Generator[Session, None, None]:
    session = MagicMock()
    session.execute.side_effect = RuntimeError("db down")
    yield session


app = create_app()
app.dependency_overrides[get_db] = _override_get_db
client = TestClient(app)


def test_health() -> None:
    """Test that health endpoint reports ok when DB is reachable."""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "ok"}


def test_health_database_error() -> None:
    """Test that health endpoint reports database error without crashing."""
    app.dependency_overrides[get_db] = _broken_db
    try:
        response = client.get("/api/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok", "database": "error"}
    finally:
        app.dependency_overrides[get_db] = _override_get_db
