"""Tests for tsrv.001 XML generation."""

from datetime import date
from decimal import Decimal

from lc_translator.mapping import map_lc_to_tsrv001
from lc_translator.models import LetterOfCredit, Money, Party, Port
from lc_translator.mx import Tsrv001Generator


def test_generate_includes_amount_and_parties() -> None:
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
    xml = Tsrv001Generator().generate(mapped)
    assert "UdrtkgIssnc" in xml
    assert 'Ccy="EUR"' in xml
    assert "10000.00" in xml
    assert "Acme" in xml
    assert "Global" in xml
    assert "Bank" in xml
