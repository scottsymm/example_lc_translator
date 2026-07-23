"""Fake Letter of Credit generator."""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal
from random import Random
from typing import Optional

from faker import Faker

from lc_translator.models import LetterOfCredit, Money, Party, Port

_CURRENCIES = ["USD", "EUR", "GBP"]
_PORTS: list[tuple[str, str]] = [
    ("Port of Long Beach", "US"),
    ("Port of Rotterdam", "NL"),
    ("Port of Hamburg", "DE"),
    ("Port of Singapore", "SG"),
    ("Port of Shanghai", "CN"),
]


def _make_bic(rng: Random, faker: Faker) -> str:
    """Generate an 8-character BIC code."""
    letters = "".join(rng.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ") for _ in range(4))
    country = faker.random_element(elements=("US", "NL", "DE", "SG", "CN", "GB"))
    suffix = "".join(rng.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789") for _ in range(2))
    return f"{letters}{country}{suffix}"


def generate_lc(seed: Optional[int] = None) -> LetterOfCredit:
    """Generate a realistic Letter of Credit.

    Args:
        seed: Optional random seed for reproducible output.

    Returns:
        A populated LetterOfCredit instance.
    """
    rng = Random(seed) if seed is not None else Random()
    faker = Faker()
    faker.seed_instance(rng.randint(0, 2**32 - 1))

    issue_date = date.today()
    expiry_date = issue_date + timedelta(days=rng.randint(30, 180))
    currency = rng.choice(_CURRENCIES)
    amount = Decimal(rng.randint(10_000, 5_000_000)) / 100

    port_name, port_country = rng.choice(_PORTS)

    def party() -> Party:
        return Party(
            name=faker.company(),
            address=faker.address().replace("\n", " "),
            bic=_make_bic(rng, faker),
        )

    return LetterOfCredit(
        lc_number=f"LC{faker.uuid4().replace('-', '').upper()[:14]}",
        issue_date=issue_date,
        expiry_date=expiry_date,
        expiry_place=Port(name=port_name, country=port_country),
        applicant=party(),
        beneficiary=party(),
        issuing_bank=party(),
        currency_amount=Money(currency=currency, amount=amount),
        port_of_loading=Port(name=port_name, country=port_country),
    )
