"""Serialize a LetterOfCredit to SWIFT MT700 text."""

from __future__ import annotations

from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from lc_translator.exceptions import Mt700FormatError
from lc_translator.models import LetterOfCredit, Party

_LINE_LIMIT = 65
_ADDRESS_LINE_LIMIT = 35


def _prefix_lines(text: str, prefix: str, limit: int) -> list[str]:
    """Break text into lines of at most `limit` characters and prefix each."""
    lines: list[str] = []
    for raw_line in text.split("\n"):
        for i in range(0, len(raw_line), limit):
            lines.append(f"{prefix}{raw_line[i : i + limit]}")
    return lines


def _fmt_tag(tag: str, value: str, limit: int = _LINE_LIMIT) -> str:
    """Format a single-line tag; raises if value exceeds limit."""
    stripped = value.rstrip()
    if len(stripped) > limit:
        raise Mt700FormatError(f"Tag {tag} value exceeds {limit} characters: {stripped[:20]}...")
    return f"{tag}{stripped}"


def _fmt_date(d: date) -> str:
    """Format date as SWIFT YYMMDD."""
    return d.strftime("%y%m%d")


def _fmt_amount(amount: Decimal) -> str:
    """Format amount using comma decimal separator, no thousands separators."""
    quantized = amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    text = str(quantized)
    return text.replace(".", ",")


def _fmt_party(tag: str, party: Party) -> list[str]:
    """Format a party block for MT700 tags :50: or :59:."""
    lines: list[str] = [tag]
    # First name line starts with '/' so reserve one character for the slash.
    name_lines = _prefix_lines(party.name, "", _ADDRESS_LINE_LIMIT - 1)
    if name_lines:
        name_lines[0] = "/" + name_lines[0].lstrip("/")
    lines.extend(name_lines)
    lines.extend(_prefix_lines(party.address, "", _ADDRESS_LINE_LIMIT))
    return lines


class Mt700Serializer:
    """Convert a LetterOfCredit to a raw MT700 text block."""

    def serialize(self, lc: LetterOfCredit) -> str:
        """Return an MT700 string representing the LC."""
        lines: list[str] = []

        lines.append(_fmt_tag(":20:", lc.lc_number))
        lines.append(_fmt_tag(":31C:", _fmt_date(lc.issue_date)))
        lines.append(_fmt_tag(":31D:", f"{_fmt_date(lc.expiry_date)} {lc.expiry_place.name}"))

        lines.extend(_fmt_party(":50:", lc.applicant))
        lines.extend(_fmt_party(":59:", lc.beneficiary))

        amount_value = f"{lc.currency_amount.currency}{_fmt_amount(lc.currency_amount.amount)}"
        lines.append(_fmt_tag(":32B:", amount_value))

        tolerance = "05/05" if lc.tolerance else "00/00"
        lines.append(_fmt_tag(":39A:", tolerance))

        lines.append(_fmt_tag(":72:", ""))

        return "\r\n".join(lines)
