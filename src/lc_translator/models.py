"""Domain models for Letter of Credit translation."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, field_validator, model_validator


class Port(BaseModel):
    """A port of loading or place."""

    name: str = Field(..., min_length=1)
    country: Optional[str] = Field(None, min_length=2, max_length=2)

    @field_validator("country")
    @classmethod
    def _uppercase_country(cls, value: Optional[str]) -> Optional[str]:
        return value.upper() if value else None


class Money(BaseModel):
    """A monetary amount with ISO 4217 currency code."""

    currency: str = Field(..., min_length=3, max_length=3)
    amount: Decimal = Field(..., gt=0, decimal_places=2)

    @field_validator("currency")
    @classmethod
    def _uppercase_currency(cls, value: str) -> str:
        return value.upper()


class Party(BaseModel):
    """A corporate party in a Letter of Credit (applicant, beneficiary, bank)."""

    name: str = Field(..., min_length=1)
    address: str = Field(..., min_length=1)
    bic: Optional[str] = Field(None, min_length=8, max_length=11)


class LetterOfCredit(BaseModel):
    """Agnostic representation of a Documentary Credit."""

    lc_number: str = Field(..., min_length=1, max_length=16)
    issue_date: date
    expiry_date: date
    expiry_place: Port
    applicant: Party
    beneficiary: Party
    issuing_bank: Party
    advising_bank: Optional[Party] = None
    currency_amount: Money
    port_of_loading: Port
    tolerance: int = Field(0, ge=-5, le=5)

    @model_validator(mode="after")
    def _expiry_after_issue(self) -> LetterOfCredit:
        if self.expiry_date < self.issue_date:
            raise ValueError("expiry_date must be on or after issue_date")
        return self

    @model_validator(mode="after")
    def _lc_number_no_colons(self) -> LetterOfCredit:
        if ":" in self.lc_number:
            raise ValueError("lc_number must not contain ':'")
        return self
