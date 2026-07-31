"""Tests for the validate endpoints."""

from fastapi.testclient import TestClient
from lc_translator_api.main import create_app
from lc_translator_core.generator import generate_lc
from lc_translator_core.mt700 import Mt700Serializer

client = TestClient(create_app())


def test_validate_mt() -> None:
    """Test test validate mt."""
    lc = generate_lc(seed=1)
    mt_text = Mt700Serializer().serialize(lc)
    response = client.post("/api/validate-mt", json={"mt700": mt_text})
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is True


def test_validate_mt_missing_tag() -> None:
    """Test test validate mt missing tag."""
    response = client.post("/api/validate-mt", json={"mt700": ":20:LC123"})
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is False
    assert any("31C" in err for err in data["errors"])


def test_validate_mx_invalid_xml() -> None:
    """Test test validate mx invalid xml."""
    response = client.post("/api/validate-mx", json={"mx_xml": "<root/>"})
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is False
    assert "validation" in data["errors"][0].lower()
