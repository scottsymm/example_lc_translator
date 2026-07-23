"""Map a LetterOfCredit to ISO 20022 tsrv.001 data structures."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from lc_translator.models import LetterOfCredit, Party


@dataclass
class Tsrv001MappedLc:
    """Intermediate representation for tsrv.001 (UndertakingIssuance) generation."""

    lc_number: str
    issue_date: date
    expiry_date: date
    undertaking_name: str  # e.g. STBY or DGAR
    issuance_type: str  # e.g. ISSU
    applicant: Party
    issuer: Party
    beneficiary: Party
    currency: str
    amount: Decimal
    governing_rule: str  # e.g. UCPR
    terms: str


def map_lc_to_tsrv001(lc: LetterOfCredit) -> Tsrv001MappedLc:
    """Translate an agnostic LC into tsrv.001 field values."""
    return Tsrv001MappedLc(
        lc_number=lc.lc_number,
        issue_date=lc.issue_date,
        expiry_date=lc.expiry_date,
        undertaking_name="STBY",
        issuance_type="ISSU",
        applicant=lc.applicant,
        issuer=lc.issuing_bank,
        beneficiary=lc.beneficiary,
        currency=lc.currency_amount.currency,
        amount=lc.currency_amount.amount,
        governing_rule="UCPR",
        terms=(
            f"Documentary credit issued for goods loaded at {lc.port_of_loading.name}. "
            f"Amount tolerance: {lc.tolerance:.0f}%."
        ),
    )
