"""Tests for API health endpoint."""

from fastapi.testclient import TestClient
from lc_translator_api.main import create_app

client = TestClient(create_app())


def test_health() -> None:
    """Test test health."""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
