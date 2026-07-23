"""Tests for MT-to-MX mapping."""

from datetime import date
from decimal import Decimal

from lc_translator.mapping import map_lc_to_tsrv001
from lc_translator.models import LetterOfCredit, Money, Party, Port


def test_map_lc_copies_core_fields() -> None:
    lc = LetterOfCredit(
        lc_number="LC001",
        issue_date=date(2026, 1, 15),
        expiry_date=date(2026, 4, 15),
        expiry_place=Port(name="Rotterdam"),
        applicant=Party(name="Acme", address="NYC"),
        beneficiary=Party(name="Global", address="Rotterdam"),
        issuing_bank=Party(name="Bank", address="NYC"),
        currency_amount=Money(currency="EUR", amount=Decimal("10000.00")),
        port_of_loading=Port(name="Rotterdam"),
    )
    mapped = map_lc_to_tsrv001(lc)
    assert mapped.lc_number == "LC001"
    assert mapped.currency == "EUR"
    assert mapped.issuer.name == "Bank"
    assert mapped.beneficiary.name == "Global"
    assert mapped.undertaking_name == "STBY"
    assert mapped.issuance_type == "ISSU"
