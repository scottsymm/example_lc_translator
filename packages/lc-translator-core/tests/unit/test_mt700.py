"""Tests for MT700 serializer, parser, and validator."""

from datetime import date
from decimal import Decimal

from lc_translator_core.generator import generate_lc
from lc_translator_core.models import LetterOfCredit, Money, Party, Port
from lc_translator_core.mt700 import Mt700Parser, Mt700Serializer, Mt700Validator


def _sample_lc() -> LetterOfCredit:
    return LetterOfCredit(
        lc_number="LC2026000001",
        issue_date=date(2026, 1, 15),
        expiry_date=date(2026, 4, 15),
        expiry_place=Port(name="Rotterdam", country="NL"),
        applicant=Party(name="Acme Imports Inc.", address="123 Main St"),
        beneficiary=Party(name="Global Exports Ltd.", address="456 Harbor Rd"),
        issuing_bank=Party(name="First National Bank", address="789 Wall St"),
        currency_amount=Money(currency="USD", amount=Decimal("150000.00")),
        port_of_loading=Port(name="Port of Long Beach", country="US"),
    )


def test_serialize_then_parse_roundtrip() -> None:
    """Test test serialize then parse roundtrip."""
    original = _sample_lc()
    mt_text = Mt700Serializer().serialize(original)
    result = Mt700Parser().parse(mt_text)
    assert result.ok(), result.errors
    recovered = result.lc
    assert recovered is not None
    assert recovered.lc_number == original.lc_number
    assert recovered.currency_amount.amount == original.currency_amount.amount


def test_missing_required_tags_reported() -> None:
    """Test test missing required tags reported."""
    result = Mt700Parser().parse(":20:LC123")
    assert not result.ok()
    assert any("31C" in err for err in result.errors)


def test_validator_detects_long_line() -> None:
    """Test test validator detects long line."""
    long_line = ":20:" + "x" * 80
    report = Mt700Validator().validate(long_line)
    assert not report.valid
    assert any("exceeds" in err for err in report.errors)


def test_generated_lc_serializes() -> None:
    """Test test generated lc serializes."""
    lc = generate_lc(seed=1)
    text = Mt700Serializer().serialize(lc)
    assert ":20:" in text
    assert ":32B:" in text
