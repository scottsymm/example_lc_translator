"""Tests for the fake LC generator."""

from lc_translator_core.generator import generate_lc


def test_generate_lc_without_seed() -> None:
    """Test test generate lc without seed."""
    lc = generate_lc()
    assert lc.lc_number.startswith("LC")
    assert lc.applicant.bic is not None
    assert len(lc.applicant.bic) == 8


def test_generate_lc_with_seed_is_deterministic() -> None:
    """Test test generate lc with seed is deterministic."""
    first = generate_lc(seed=42)
    second = generate_lc(seed=42)
    assert first == second
