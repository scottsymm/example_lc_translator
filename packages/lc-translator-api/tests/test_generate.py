"""Tests for the generate endpoint."""

from fastapi.testclient import TestClient
from lc_translator_api.main import create_app

client = TestClient(create_app())


def test_generate_with_seed() -> None:
    """Test test generate with seed."""
    response = client.post("/api/generate", json={"seed": 42})
    assert response.status_code == 200
    data = response.json()
    assert data["lc_number"]
    assert ":20:" in data["mt700"]
    assert "<Document" in data["mx_xml"]
    assert data["mt700_valid"] is True
