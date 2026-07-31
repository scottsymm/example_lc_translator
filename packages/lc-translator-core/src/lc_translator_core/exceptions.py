"""Exceptions and result types for lc-translator."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from lc_translator_core.models import LetterOfCredit


class LcTranslatorError(Exception):
    """Base exception for the lc-translator package."""


class Mt700FormatError(LcTranslatorError):
    """Raised when MT700 text violates formatting rules."""


class XsdValidationError(LcTranslatorError):
    """Raised when MX XML fails XSD validation."""


@dataclass
class ParseResult:
    """Result of a best-effort MT700 parse.

    Attributes:
        lc: The recovered Letter of Credit, if parsing produced a valid model.
        warnings: Non-fatal issues encountered during parsing.
        errors: Fatal issues that prevented full recovery.
    """

    lc: Optional[LetterOfCredit] = None
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def ok(self) -> bool:
        """Return True if a model was recovered and there are no errors."""
        return self.lc is not None and not self.errors
