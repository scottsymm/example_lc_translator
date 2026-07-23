"""Tests for the fake LC generator."""

from lc_translator.generator import generate_lc


def test_generate_lc_without_seed() -> None:
    lc = generate_lc()
    assert lc.lc_number.startswith("LC")
    assert lc.applicant.bic is not None
    assert len(lc.applicant.bic) == 8


def test_generate_lc_with_seed_is_deterministic() -> None:
    first = generate_lc(seed=42)
    second = generate_lc(seed=42)
    assert first == second
