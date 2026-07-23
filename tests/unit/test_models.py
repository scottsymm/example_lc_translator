"""Tests for Pydantic domain models."""

from datetime import date, timedelta
from decimal import Decimal

import pytest

from lc_translator.models import LetterOfCredit, Money, Party, Port


def _valid_lc(**overrides: object) -> LetterOfCredit:
    defaults = {
        "lc_number": "LC1234567890",
        "issue_date": date.today(),
        "expiry_date": date.today() + timedelta(days=90),
        "expiry_place": Port(name="Rotterdam"),
        "applicant": Party(name="Acme Imports", address="123 Main St\nNew York"),
        "beneficiary": Party(name="Global Exports", address="456 Harbor Rd\nRotterdam"),
        "issuing_bank": Party(name="First National Bank", address="789 Wall St\nNew York"),
        "currency_amount": Money(currency="USD", amount=Decimal("150000.00")),
        "port_of_loading": Port(name="Port of Long Beach", country="US"),
    }
    defaults.update(overrides)
    return LetterOfCredit(**defaults)


def test_valid_letter_of_credit() -> None:
    lc = _valid_lc()
    assert lc.lc_number == "LC1234567890"
    assert lc.currency_amount.currency == "USD"


def test_currency_is_uppercased() -> None:
    money = Money(currency="usd", amount=Decimal("1000.00"))
    assert money.currency == "USD"


def test_country_is_uppercased() -> None:
    port = Port(name="Port of Long Beach", country="us")
    assert port.country == "US"


def test_expiry_before_issue_raises() -> None:
    today = date.today()
    with pytest.raises(ValueError):
        _valid_lc(issue_date=today + timedelta(days=1), expiry_date=today)


def test_lc_number_cannot_contain_colon() -> None:
    with pytest.raises(ValueError):
        _valid_lc(lc_number="LC:123")
