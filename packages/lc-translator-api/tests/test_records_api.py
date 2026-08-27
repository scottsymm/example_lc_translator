"""Tests for records API endpoints."""

from __future__ import annotations

from collections.abc import Generator
from typing import Any

from fastapi.testclient import TestClient
from lc_translator_api.dependencies import get_db
from lc_translator_api.main import create_app
from lc_translator_api.models.record import Base
from sqlalchemy import StaticPool, create_engine
from sqlalchemy.orm import Session, sessionmaker

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


app = create_app()
app.dependency_overrides[get_db] = _override_get_db
client = TestClient(app)


def _sample_payload() -> dict[str, Any]:
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
    """Test POST /records creates a record."""
    response = client.post("/api/records", json=_sample_payload())
    assert response.status_code == 201
    data = response.json()
    assert data["id"]
    assert data["source_type"] == "generated"


def test_list_records() -> None:
    """Test GET /records lists records."""
    client.post("/api/records", json=_sample_payload())
    response = client.get("/api/records")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1


def test_get_record() -> None:
    """Test GET /records/{id} fetches a record."""
    created = client.post("/api/records", json=_sample_payload()).json()
    response = client.get(f"/api/records/{created['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


def test_get_record_not_found() -> None:
    """Test GET /records/{id} returns 404 for missing record."""
    response = client.get("/api/records/not-real")
    assert response.status_code == 404


def test_update_record() -> None:
    """Test PUT /records/{id} updates a record title."""
    created = client.post("/api/records", json=_sample_payload()).json()
    response = client.put(f"/api/records/{created['id']}", json={"title": "Updated"})
    assert response.status_code == 200
    assert response.json()["title"] == "Updated"


def test_delete_record() -> None:
    """Test DELETE /records/{id} removes a record."""
    created = client.post("/api/records", json=_sample_payload()).json()
    response = client.delete(f"/api/records/{created['id']}")
    assert response.status_code == 204
    assert client.get(f"/api/records/{created['id']}").status_code == 404


def test_rerun_generated_record() -> None:
    """Test POST /records/{id}/rerun re-runs a generated record."""
    created = client.post("/api/records", json=_sample_payload()).json()
    response = client.post(f"/api/records/{created['id']}/rerun")
    assert response.status_code == 200
    data = response.json()
    assert ":20:" in data["mt700"]
    assert "<Document" in data["mx_xml"]


def test_rerun_translated_record() -> None:
    """Test POST /records/{id}/rerun re-runs a translated record."""
    client.post("/api/generate", json={"seed": 42})
    generate_response = client.post("/api/generate", json={"seed": 42}).json()
    created = client.post(
        "/api/records",
        json={
            "source_type": "translated",
            "mt700_input": generate_response["mt700"],
        },
    ).json()
    response = client.post(f"/api/records/{created['id']}/rerun")
    assert response.status_code == 200
    data = response.json()
    assert "<Document" in data["mx_xml"]
