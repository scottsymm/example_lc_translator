"""Tests for records API endpoints."""

from __future__ import annotations

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


def _override_get_db() -> Session:
    session = _TestSessionLocal()
    try:
        yield session
    finally:
        session.close()


app = create_app()
app.dependency_overrides[get_db] = _override_get_db
client = TestClient(app)


def _sample_payload() -> dict:
    return {
        "source_type": "generated",
        "generated_seed": 42,
        "generated_strict": False,
        "mx_xml": "<Document/>",
        "validation_result": {
            "mt700_valid": True,
            "mt700_errors": [],
            "mt700_warnings": [],
            "mx_valid": True,
            "mx_errors": [],
        },
    }


def test_create_record() -> None:
    response = client.post("/api/records", json=_sample_payload())
    assert response.status_code == 201
    data = response.json()
    assert data["id"]
    assert data["source_type"] == "generated"


def test_list_records() -> None:
    client.post("/api/records", json=_sample_payload())
    response = client.get("/api/records")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1


def test_get_record() -> None:
    created = client.post("/api/records", json=_sample_payload()).json()
    response = client.get(f"/api/records/{created['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


def test_get_record_not_found() -> None:
    response = client.get("/api/records/not-real")
    assert response.status_code == 404


def test_update_record() -> None:
    created = client.post("/api/records", json=_sample_payload()).json()
    response = client.put(f"/api/records/{created['id']}", json={"title": "Updated"})
    assert response.status_code == 200
    assert response.json()["title"] == "Updated"


def test_delete_record() -> None:
    created = client.post("/api/records", json=_sample_payload()).json()
    response = client.delete(f"/api/records/{created['id']}")
    assert response.status_code == 204
    assert client.get(f"/api/records/{created['id']}").status_code == 404
