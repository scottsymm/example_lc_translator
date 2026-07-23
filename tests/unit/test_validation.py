"""Tests for XSD validation."""

from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from lc_translator.exceptions import XsdValidationError
from lc_translator.mapping import map_lc_to_tsrv001
from lc_translator.models import LetterOfCredit, Money, Party, Port
from lc_translator.mx import Tsrv001Generator
from lc_translator.validation import XsdValidator


def test_validator_unavailable_when_no_schema() -> None:
    validator = XsdValidator(xsd_path=Path("/does/not/exist.xsd"))
    assert not validator.is_available()


def test_validate_raises_without_schema() -> None:
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
    xml = Tsrv001Generator().generate(map_lc_to_tsrv001(lc))
    validator = XsdValidator(xsd_path=Path("/does/not/exist.xsd"))
    with pytest.raises(XsdValidationError):
        validator.validate(xml)
