"""Parse a raw MT700 text block back into a LetterOfCredit."""

from __future__ import annotations

import re
from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Optional

from lc_translator_core.exceptions import ParseResult
from lc_translator_core.models import LetterOfCredit, Money, Party, Port

_TAG_PATTERN = re.compile(r"^:(\d{2}[A-Z]?):(.*)$")


def _parse_yy_mm_dd(value: str) -> Optional[date]:
    """Parse YYMMDD into a date."""
    value = value.strip()
    if len(value) != 6 or not value.isdigit():
        return None
    try:
        return date(2000 + int(value[0:2]), int(value[2:4]), int(value[4:6]))
    except ValueError:
        return None


def _parse_amount(value: str) -> Optional[Decimal]:
    """Parse a SWIFT amount string with comma decimal separator."""
    cleaned = value.replace(".", "").replace(",", ".")
    try:
        return Decimal(cleaned)
    except InvalidOperation:
        return None


class Mt700Parser:
    """Best-effort parser for MT700 text."""

    def parse(self, text: str) -> ParseResult:
        """Parse MT700 text and return a ParseResult with warnings and errors."""
        warnings: list[str] = []
        errors: list[str] = []

        lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
        lines = [line for line in lines if line.strip()]

        sections: dict[str, list[str]] = {}
        current_tag: Optional[str] = None

        for line in lines:
            match = _TAG_PATTERN.match(line)
            if match:
                tag, value = match.groups()
                current_tag = tag
                if value.strip():
                    sections.setdefault(current_tag, []).append(value)
            elif current_tag is not None:
                sections.setdefault(current_tag, []).append(line)
            else:
                warnings.append(f"Untagged line before first tag: {line[:40]}")

        try:
            lc = self._build_lc(sections, warnings, errors)
        except ValueError as exc:
            errors.append(str(exc))
            lc = None

        return ParseResult(lc=lc, warnings=warnings, errors=errors)

    def _build_lc(
        self,
        sections: dict[str, list[str]],
        warnings: list[str],
        errors: list[str],
    ) -> LetterOfCredit:
        """Build a LetterOfCredit from parsed sections."""
        required_tags = ["20", "31C", "31D", "50", "59", "32B"]
        for tag in required_tags:
            if tag not in sections:
                errors.append(f"Required tag :{tag}: is missing")

        if errors:
            raise ValueError("Cannot build LC: required tags missing")

        lc_number = " ".join(sections.get("20", ["UNKNOWN"]))
        issue_raw = sections.get("31C", [""])[0].strip()
        issue_date = _parse_yy_mm_dd(issue_raw)
        if issue_date is None:
            errors.append(f"Invalid issue date: {issue_raw}")

        expiry_parts = sections.get("31D", [""])[0].strip().split(" ", 1)
        expiry_date = _parse_yy_mm_dd(expiry_parts[0])
        expiry_place = expiry_parts[1] if len(expiry_parts) > 1 else "UNKNOWN"
        if expiry_date is None:
            errors.append(f"Invalid expiry date: {expiry_parts[0]}")

        applicant_lines = sections.get("50", [])
        beneficiary_lines = sections.get("59", [])
        amount_raw = sections.get("32B", [""])[0].strip()

        if len(amount_raw) < 3:
            errors.append(f"Invalid currency/amount: {amount_raw}")
            currency, amount = "XXX", Decimal("0")
        else:
            currency = amount_raw[:3]
            amount = _parse_amount(amount_raw[3:]) or Decimal("0")
            if amount <= 0:
                errors.append(f"Invalid amount: {amount_raw}")

        if errors:
            raise ValueError("Cannot build LC: data errors")

        applicant = self._party_from_lines(applicant_lines)
        beneficiary = self._party_from_lines(beneficiary_lines)

        return LetterOfCredit(
            lc_number=lc_number,
            issue_date=issue_date,
            expiry_date=expiry_date,
            expiry_place=Port(name=expiry_place),
            applicant=applicant,
            beneficiary=beneficiary,
            issuing_bank=applicant,  # Best-effort fallback
            currency_amount=Money(currency=currency, amount=amount),
            port_of_loading=Port(name="Unknown"),
        )

    def _party_from_lines(self, lines: list[str]) -> Party:
        """Build a Party from MT tag lines, stripping leading slash on name."""
        name = lines[0].lstrip("/") if lines else "UNKNOWN"
        address = "\n".join(lines[1:]) if len(lines) > 1 else "Unknown"
        return Party(name=name, address=address)
