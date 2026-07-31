"""Tests for the translate endpoint."""

from fastapi.testclient import TestClient
from lc_translator_api.main import create_app
from lc_translator_core.generator import generate_lc
from lc_translator_core.mt700 import Mt700Serializer

client = TestClient(create_app())


def test_translate_mt700_to_mx() -> None:
    """Test test translate mt700 to mx."""
    lc = generate_lc(seed=1)
    mt_text = Mt700Serializer().serialize(lc)
    response = client.post("/api/mt-to-mx", json={"mt700": mt_text})
    assert response.status_code == 200
    data = response.json()
    assert "<Document" in data["mx_xml"]
    assert not data["errors"]
