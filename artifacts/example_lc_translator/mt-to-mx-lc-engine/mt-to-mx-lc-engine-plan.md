# MT-to-MX Letter of Credit Translation Engine — Implementation Plan

*Created: 2026-07-23*

**Goal:** Build a runnable Python CLI that generates a Letter of Credit, emits MT700 and ISO 20022 camt.087 XML, and validates both.

**Architecture:** A vertical-slice library in `src/lc_translator/` with Pydantic models, Faker-based generation, SWIFT MT700 serialize/parse/validate, MT-to-MX mapping, lxml-based MX generation, and XSD validation. A `typer` CLI orchestrates the pipeline.

**Tech Stack:** Python 3.9+, Pydantic v2, lxml, Faker, typer, uv, ruff, mypy, pytest, freezegun.

**Source:** `/Users/jobofish/code/python/artifacts/code/python/mt-to-mx-lc-engine/mt-to-mx-lc-engine-design.md`


## File Map

| File | Action | Responsibility |
|---|---|---|
| `pyproject.toml` | Create | Project metadata, dependencies, ruff/mypy/pytest config |
| `README.md` | Create | Project overview, domain primer, run instructions |
| `scripts/fetch_xsd.py` | Create | Download/cache official camt.087 XSD |
| `src/lc_translator/__init__.py` | Create | Public API exports and version |
| `src/lc_translator/__version__.py` | Create | Single source of truth for version |
| `src/lc_translator/exceptions.py` | Create | Custom exception classes and parse result type |
| `src/lc_translator/models.py` | Create | Pydantic domain models (`LetterOfCredit`, `Party`, `Money`, `Port`) |
| `src/lc_translator/generator.py` | Create | Faker-based LC generator with seed support |
| `src/lc_translator/mt700/serializer.py` | Create | Serialize `LetterOfCredit` to MT700 text |
| `src/lc_translator/mt700/parser.py` | Create | Parse MT700 text to `LetterOfCredit` with warnings/errors |
| `src/lc_translator/mt700/validator.py` | Create | MT700 structure validation (line lengths, required tags) |
| `src/lc_translator/mt700/__init__.py` | Create | Public exports for MT700 subpackage |
| `src/lc_translator/mapping.py` | Create | Map `LetterOfCredit` fields to camt.087 XML data |
| `src/lc_translator/mx.py` | Create | Generate camt.087 XML from mapped data |
| `src/lc_translator/validation.py` | Create | XSD loading, caching, and validation |
| `src/lc_translator/cli.py` | Create | `typer` CLI commands |
| `tests/conftest.py` | Create | Shared deterministic fixtures |
| `tests/unit/test_models.py` | Create | Unit tests for Pydantic models |
| `tests/unit/test_generator.py` | Create | Unit tests for fake generator |
| `tests/unit/test_mt700.py` | Create | Unit tests for MT700 serializer and parser |
| `tests/unit/test_mapping.py` | Create | Unit tests for MT-to-MX mapping |
| `tests/unit/test_mx.py` | Create | Unit tests for MX generation |
| `tests/integration/test_pipeline.py` | Create | End-to-end pipeline test |


## Tasks

### Task 1: Initialize project structure and packaging

**Files:**
- Create: `pyproject.toml`
- Create: `src/lc_translator/__init__.py`
- Create: `src/lc_translator/__version__.py`

**Step 1:** Write `pyproject.toml` with project metadata, dependency groups, and tool configs.

```toml
[project]
name = "lc-translator"
version = "0.1.0"
description = "MT700 to camt.087 Letter of Credit translation demo"
requires-python = ">=3.9"
authors = [{ name = "Your Name", email = "you@example.com" }]
readme = "README.md"
license = { text = "MIT" }
dependencies = [
    "pydantic>=2.0",
    "lxml>=4.9",
    "faker>=20.0",
    "typer[all]>=0.9",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
    "freezegun>=1.0",
    "ruff>=0.1.0",
    "mypy>=1.0",
]

[project.scripts]
lc-translator = "lc_translator.cli:app"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.ruff]
line-length = 100
target-version = "py39"

[tool.ruff.lint]
select = ["E", "W", "F", "I", "B", "C4", "UP", "SIM", "D"]
ignore = ["D100", "D104", "E501"]

[tool.ruff.lint.pydocstyle]
convention = "google"

[tool.ruff.format]
quote-style = "double"
indent-style = "space"

[tool.mypy]
python_version = "3.9"
strict = true
warn_return_any = true
warn_unused_ignores = true
disallow_untyped_defs = true

[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
addopts = "--cov=lc_translator --cov-report=term-missing"
```

**Step 2:** Create `src/lc_translator/__version__.py`.

```python
"""Version information."""

__version__ = "0.1.0"
```

**Step 3:** Create `src/lc_translator/__init__.py`.

```python
"""MT700-to-camt.087 Letter of Credit translation engine."""

from lc_translator.__version__ import __version__
from lc_translator.exceptions import (
    LcTranslatorError,
    Mt700FormatError,
    ParseResult,
    XsdValidationError,
)
from lc_translator.generator import generate_lc
from lc_translator.models import LetterOfCredit, Money, Party, Port

__all__ = [
    "__version__",
    "generate_lc",
    "LetterOfCredit",
    "Money",
    "Party",
    "Port",
    "LcTranslatorError",
    "Mt700FormatError",
    "ParseResult",
    "XsdValidationError",
]
```

**Step 4: Verify**

Run:
```bash
uv sync --extra dev
uv run python -c "import lc_translator; print(lc_translator.__version__)"
```

Expected: `0.1.0` printed without import errors.

**Step 5: Commit**

```bash
git add pyproject.toml src/lc_translator/__init__.py src/lc_translator/__version__.py
git commit -m "chore: initialize project structure and packaging"
```


### Task 2: Define custom exceptions and parse result

**Files:**
- Create: `src/lc_translator/exceptions.py`

**Step 1:** Implement base exception hierarchy and `ParseResult`.

```python
"""Exceptions and result types for lc-translator."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lc_translator.models import LetterOfCredit


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

    lc: LetterOfCredit | None = None
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def ok(self) -> bool:
        """Return True if a model was recovered and there are no errors."""
        return self.lc is not None and not self.errors
```

**Step 2: Verify**

Run:
```bash
uv run python -c "from lc_translator.exceptions import ParseResult; print(ParseResult())"
```

Expected: a `ParseResult` dataclass is printed.

**Step 3: Commit**

```bash
git add src/lc_translator/exceptions.py
git commit -m "feat: add exception hierarchy and parse result type"
```


### Task 3: Define Pydantic domain models

**Files:**
- Create: `src/lc_translator/models.py`
- Create: `tests/unit/test_models.py`

**Step 1:** Implement domain models.

```python
"""Domain models for Letter of Credit translation."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator


class Port(BaseModel):
    """A port of loading or place."""

    name: str = Field(..., min_length=1)
    country: str | None = Field(None, min_length=2, max_length=2)

    @field_validator("country")
    @classmethod
    def _uppercase_country(cls, value: str | None) -> str | None:
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
    bic: str | None = Field(None, min_length=8, max_length=11)


class LetterOfCredit(BaseModel):
    """Agnostic representation of a Documentary Credit."""

    lc_number: str = Field(..., min_length=1, max_length=16)
    issue_date: date
    expiry_date: date
    expiry_place: Port
    applicant: Party
    beneficiary: Party
    issuing_bank: Party
    advising_bank: Party | None = None
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
```

**Step 2:** Create tests.

```python
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
```

**Step 3: Verify**

Run:
```bash
uv run pytest tests/unit/test_models.py -v
```

Expected: 5 tests passing.

**Step 4: Commit**

```bash
git add src/lc_translator/models.py tests/unit/test_models.py
git commit -m "feat: add Pydantic domain models for LC, parties, money, and ports"
```


### Task 4: Build fake LC generator

**Files:**
- Create: `src/lc_translator/generator.py`
- Create: `tests/unit/test_generator.py`

**Step 1:** Implement generator.

```python
"""Fake Letter of Credit generator."""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal
from random import Random

from faker import Faker

from lc_translator.models import LetterOfCredit, Money, Party, Port

_CURRENCIES = ["USD", "EUR", "GBP"]
_PORTS = [
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


def generate_lc(seed: int | None = None) -> LetterOfCredit:
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
```

**Step 2:** Create tests.

```python
"""Tests for the fake LC generator."""

from lc_translator.generator import generate_lc


def test_generate_lc_without_seed() -> None:
    lc = generate_lc()
    assert lc.lc_number.startswith("LC")
    assert lc.applicant.bic is not None
    assert len(lc.applicant.bic) == 8


def test_generate_lc_with_seed_is_deterministic() -> None:
    first = generate_lc(seed=42)
    second = generate_lc(seed=42)
    assert first == second
```

**Step 3: Verify**

Run:
```bash
uv run pytest tests/unit/test_generator.py -v
```

Expected: 2 tests passing.

**Step 4: Commit**

```bash
git add src/lc_translator/generator.py tests/unit/test_generator.py
git commit -m "feat: add deterministic fake LC generator"
```


### Task 5: Implement MT700 serializer

**Files:**
- Create: `src/lc_translator/mt700/serializer.py`
- Modify: `src/lc_translator/mt700/__init__.py` (create)

**Step 1:** Implement serializer.

```python
"""Serialize a LetterOfCredit to SWIFT MT700 text."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from lc_translator.exceptions import Mt700FormatError
from lc_translator.models import LetterOfCredit

_LINE_LIMIT = 65
_ADDRESS_LINE_LIMIT = 35


def _prefix_lines(text: str, prefix: str, limit: int) -> list[str]:
    """Break text into lines of at most `limit` characters and prefix each."""
    lines = []
    for raw_line in text.split("\n"):
        for i in range(0, len(raw_line), limit):
            lines.append(f"{prefix}{raw_line[i:i + limit]}")
    return lines


def _fmt_tag(tag: str, value: str, limit: int = _LINE_LIMIT) -> str:
    """Format a single-line tag; raises if value exceeds limit."""
    stripped = value.rstrip()
    if len(stripped) > limit:
        raise Mt700FormatError(
            f"Tag {tag} value exceeds {limit} characters: {stripped[:20]}..."
        )
    return f"{tag}{stripped}"


def _fmt_date(d: date) -> str:
    return d.strftime("%y%m%d")


def _fmt_amount(amount: Decimal) -> str:
    """Format using comma as decimal separator per SWIFT convention."""
    return f"{amount:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


class Mt700Serializer:
    """Convert a LetterOfCredit to a raw MT700 text block."""

    def serialize(self, lc: LetterOfCredit) -> str:
        """Return an MT700 string representing the LC."""
        lines: list[str] = []
        lines.append(_fmt_tag(":20:", lc.lc_number))
        lines.append(_fmt_tag(":31C:", _fmt_date(lc.issue_date)))
        lines.append(
            _fmt_tag(":31D:", f"{_fmt_date(lc.expiry_date)} {lc.expiry_place.name}")
        )
        lines.extend(_prefix_lines(lc.applicant.name, "", _ADDRESS_LINE_LIMIT))
        lines.append(f"{line}" if line.startswith("/") else f"/{line}" if idx == 0 else line)
```

Oops — the snippet above is incomplete. Correct implementation follows.

```python
"""Serialize a LetterOfCredit to SWIFT MT700 text."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from lc_translator.exceptions import Mt700FormatError
from lc_translator.models import LetterOfCredit

_LINE_LIMIT = 65
_ADDRESS_LINE_LIMIT = 35


def _prefix_lines(text: str, prefix: str, limit: int) -> list[str]:
    """Break text into lines of at most `limit` characters and prefix each."""
    lines: list[str] = []
    for raw_line in text.split("\n"):
        for i in range(0, len(raw_line), limit):
            lines.append(f"{prefix}{raw_line[i:i + limit]}")
    return lines


def _fmt_tag(tag: str, value: str, limit: int = _LINE_LIMIT) -> str:
    """Format a single-line tag; raises if value exceeds limit."""
    stripped = value.rstrip()
    if len(stripped) > limit:
        raise Mt700FormatError(
            f"Tag {tag} value exceeds {limit} characters: {stripped[:20]}..."
        )
    return f"{tag}{stripped}"


def _fmt_date(d: date) -> str:
    return d.strftime("%y%m%d")


def _fmt_amount(amount: Decimal) -> str:
    """Format using comma as decimal separator per SWIFT convention."""
    text = f"{amount:,.2f}"
    text = text.replace(",", "X").replace(".", ",").replace("X", ".")
    return text


class Mt700Serializer:
    """Convert a LetterOfCredit to a raw MT700 text block."""

    def serialize(self, lc: LetterOfCredit) -> str:
        """Return an MT700 string representing the LC."""
        lines: list[str] = []

        # :20: Documentary Credit Number
        lines.append(_fmt_tag(":20:", lc.lc_number))

        # :31C: Date of Issue
        lines.append(_fmt_tag(":31C:", _fmt_date(lc.issue_date)))

        # :31D: Date and Place of Expiry
        lines.append(
            _fmt_tag(":31D:", f"{_fmt_date(lc.expiry_date)} {lc.expiry_place.name}")
        )

        # :50: Applicant
        lines.append(":50:")
        name_lines = _prefix_lines(lc.applicant.name, "", _ADDRESS_LINE_LIMIT)
        name_lines[0] = "/" + name_lines[0] if not name_lines[0].startswith("/") else name_lines[0]
        lines.extend(name_lines)
        lines.extend(_prefix_lines(lc.applicant.address, "", _ADDRESS_LINE_LIMIT))

        # :59: Beneficiary
        lines.append(":59:")
        bname_lines = _prefix_lines(lc.beneficiary.name, "", _ADDRESS_LINE_LIMIT)
        bname_lines[0] = "/" + bname_lines[0] if not bname_lines[0].startswith("/") else bname_lines[0]
        lines.extend(bname_lines)
        lines.extend(_prefix_lines(lc.beneficiary.address, "", _ADDRESS_LINE_LIMIT))

        # :32B: Currency Code, Amount
        lines.append(
            _fmt_tag(":32B:", f"{lc.currency_amount.currency}{_fmt_amount(lc.currency_amount.amount)}")
        )

        # :39A: Percentage Credit Amount Tolerance (optional, simplified to +/- 0/0 if none)
        warn_part = "05/05" if lc.tolerance else "0/0"
        lines.append(_fmt_tag(":39A:", warn_part))

        lines.append(":72:")  # Sender to Receiver Information (empty marker)

        return "\r\n".join(lines)
```

**Step 2:** Create MT700 subpackage `__init__.py`.

```python
"""SWIFT MT700 serializer and parser."""

from lc_translator.mt700.parser import Mt700Parser, ParseResult
from lc_translator.mt700.serializer import Mt700Serializer
from lc_translator.mt700.validator import Mt700Validator

__all__ = ["Mt700Serializer", "Mt700Parser", "ParseResult", "Mt700Validator"]
```

**Step 3: Verify**

Run:
```bash
uv run python -c "from lc_translator.mt700 import Mt700Serializer; print('ok')"
```

Expected: `ok` printed.

**Step 4: Commit**

```bash
git add src/lc_translator/mt700/__init__.py src/lc_translator/mt700/serializer.py
git commit -m "feat: add MT700 serializer"
```


### Task 6: Implement MT700 parser

**Files:**
- Create: `src/lc_translator/mt700/parser.py`

**Step 1:** Implement parser.

```python
"""Parse a raw MT700 text block back into a LetterOfCredit."""

from __future__ import annotations

import re
from datetime import date
from decimal import Decimal, InvalidOperation

from lc_translator.exceptions import ParseResult
from lc_translator.models import LetterOfCredit, Money, Party, Port

_TAG_PATTERN = re.compile(r"^:(\d{2}[A-Z]?):(.*)$")


def _parse_yy_mm_dd(value: str) -> date | None:
    """Parse YYMMDD into a date."""
    try:
        return date(2000 + int(value[0:2]), int(value[2:4]), int(value[4:6]))
    except (ValueError, IndexError):
        return None


def _parse_amount(value: str) -> Decimal | None:
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

        # Normalize line endings
        lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
        lines = [line for line in lines if line.strip()]

        sections: dict[str, list[str]] = {}
        current_tag: str | None = None

        for line in lines:
            match = _TAG_PATTERN.match(line)
            if match:
                tag, value = match.groups()
                current_tag = tag
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
            issue_date=issue_date,  # type: ignore[arg-type]
            expiry_date=expiry_date,  # type: ignore[arg-type]
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
        address = "\n".join(lines[1:]) if len(lines) > 1 else ""
        return Party(name=name, address=address)
```

**Step 2: Verify**

Run:
```bash
uv run python -c "from lc_translator.mt700 import Mt700Parser; print(Mt700Parser().parse(':20:LC123\n:31C:250101'))"
```

Expected: a `ParseResult` printed with expected errors for missing tags.

**Step 3: Commit**

```bash
git add src/lc_translator/mt700/parser.py
git commit -m "feat: add best-effort MT700 parser"
```


### Task 7: Implement MT700 validator

**Files:**
- Create: `src/lc_translator/mt700/validator.py`

**Step 1:** Implement validator.

```python
"""MT700 structural validation."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

_TAG_PATTERN = re.compile(r"^:(\d{2}[A-Z]?):(.*)$")
_MT700_REQUIRED_TAGS = {"20", "31C", "31D", "50", "59", "32B"}
_LINE_LIMIT = 65
_ADDRESS_LINE_LIMIT = 35


@dataclass
class Mt700ValidationReport:
    """Report of structural checks on an MT700 message."""

    valid: bool = True
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def add_error(self, message: str) -> None:
        self.errors.append(message)
        self.valid = False

    def add_warning(self, message: str) -> None:
        self.warnings.append(message)


class Mt700Validator:
    """Validate raw MT700 text structure."""

    def validate(self, text: str) -> Mt700ValidationReport:
        """Check line lengths and required tags."""
        report = Mt700ValidationReport()
        lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
        seen_tags: set[str] = set()
        in_address_tag = False
        address_limit_window = {"50", "59"}

        for idx, raw_line in enumerate(lines, start=1):
            if not raw_line.strip():
                continue
            if len(raw_line) > _LINE_LIMIT:
                report.add_error(f"Line {idx} exceeds {_LINE_LIMIT} characters")

            match = _TAG_PATTERN.match(raw_line)
            if match:
                tag, _value = match.groups()
                seen_tags.add(tag)
                in_address_tag = tag in address_limit_window
            elif in_address_tag and len(raw_line) > _ADDRESS_LINE_LIMIT:
                report.add_warning(
                    f"Line {idx} within address tag exceeds {_ADDRESS_LINE_LIMIT} characters"
                )

        missing = _MT700_REQUIRED_TAGS - seen_tags
        for tag in sorted(missing):
            report.add_error(f"Required tag :{tag}: is missing")

        return report
```

**Step 2: Verify**

Run:
```bash
uv run python -c "
from lc_translator.mt700.validator import Mt700Validator
print(Mt700Validator().validate(':20:LC123'))
"
```

Expected: a report with `valid=False` and errors about missing tags and line length.

**Step 3: Commit**

```bash
git add src/lc_translator/mt700/validator.py
git commit -m "feat: add MT700 structure validator"
```


### Task 8: Add MT700 unit tests

**Files:**
- Create: `tests/unit/test_mt700.py`

**Step 1:** Write tests.

```python
"""Tests for MT700 serializer, parser, and validator."""

from datetime import date, timedelta
from decimal import Decimal

from lc_translator.generator import generate_lc
from lc_translator.models import LetterOfCredit, Money, Party, Port
from lc_translator.mt700 import Mt700Parser, Mt700Serializer, Mt700Validator


def _sample_lc() -> LetterOfCredit:
    return LetterOfCredit(
        lc_number="LC2026000001",
        issue_date=date(2026, 1, 15),
        expiry_date=date(2026, 4, 15),
        expiry_place=Port(name="Rotterdam", country="NL"),
        applicant=Party(name="Acme Imports Inc.", address="123 Main St"),
        beneficiary=Party(name="Global Exports Ltd.", address="456 Harbor Rd"),
        issuing_bank=Party(name="First National Bank", address="789 Wall St"),
        currency_amount=Money(currency="USD", amount=Decimal("150000.00")),
        port_of_loading=Port(name="Port of Long Beach", country="US"),
    )


def test_serialize_then_parse_roundtrip() -> None:
    original = _sample_lc()
    mt_text = Mt700Serializer().serialize(original)
    result = Mt700Parser().parse(mt_text)
    assert result.ok(), result.errors
    recovered = result.lc
    assert recovered is not None
    assert recovered.lc_number == original.lc_number
    assert recovered.currency_amount.amount == original.currency_amount.amount


def test_missing_required_tags_reported() -> None:
    result = Mt700Parser().parse(":20:LC123")
    assert not result.ok()
    assert any("31C" in err for err in result.errors)


def test_validator_detects_long_line() -> None:
    long_line = ":20:" + "x" * 80
    report = Mt700Validator().validate(long_line)
    assert not report.valid
    assert any("exceeds" in err for err in report.errors)


def test_generated_lc_serializes() -> None:
    lc = generate_lc(seed=1)
    text = Mt700Serializer().serialize(lc)
    assert ":20:" in text
    assert ":32B:" in text
```

**Step 2: Verify**

Run:
```bash
uv run pytest tests/unit/test_mt700.py -v
```

Expected: 4 tests passing.

**Step 3: Commit**

```bash
git add tests/unit/test_mt700.py
git commit -m "test: add MT700 serializer, parser, and validator tests"
```


### Task 9: Implement MT-to-MX mapping

**Files:**
- Create: `src/lc_translator/mapping.py`
- Create: `tests/unit/test_mapping.py`

**Step 1:** Implement mapping dataclass and function.

```python
"""Map a LetterOfCredit to ISO 20022 camt.087 data structures."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from lc_translator.models import LetterOfCredit


@dataclass
class Camt087MappedLc:
    """Intermediate representation for camt.087 generation."""

    credit_id: str
    creation_datetime: datetime
    expiry_date: str
    expiry_place: str
    instructed_amount: Decimal
    instructed_currency: str
    debtor_name: str
    debtor_address: str
    creditor_name: str
    creditor_address: str


def map_lc_to_camt087(lc: LetterOfCredit) -> Camt087MappedLc:
    """Translate an agnostic LC into camt.087 field values."""
    return Camt087MappedLc(
        credit_id=lc.lc_number,
        creation_datetime=datetime.combine(lc.issue_date, datetime.min.time()),
        expiry_date=lc.expiry_date.isoformat(),
        expiry_place=lc.expiry_place.name,
        instructed_amount=lc.currency_amount.amount,
        instructed_currency=lc.currency_amount.currency,
        debtor_name=lc.applicant.name,
        debtor_address=lc.applicant.address,
        creditor_name=lc.beneficiary.name,
        creditor_address=lc.beneficiary.address,
    )
```

**Step 2:** Create tests.

```python
"""Tests for MT-to-MX mapping."""

from datetime import date
from decimal import Decimal

from lc_translator.mapping import map_lc_to_camt087
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
    mapped = map_lc_to_camt087(lc)
    assert mapped.credit_id == "LC001"
    assert mapped.instructed_currency == "EUR"
    assert mapped.debtor_name == "Acme"
    assert mapped.creditor_name == "Global"
```

**Step 3: Verify**

Run:
```bash
uv run pytest tests/unit/test_mapping.py -v
```

Expected: 1 test passing.

**Step 4: Commit**

```bash
git add src/lc_translator/mapping.py tests/unit/test_mapping.py
git commit -m "feat: add MT700-to-camt.087 mapping layer"
```


### Task 10: Implement camt.087 MX generator

**Files:**
- Create: `src/lc_translator/mx.py`
- Create: `tests/unit/test_mx.py`

**Step 1:** Implement generator.

```python
"""Generate ISO 20022 camt.087 XML from a mapped Letter of Credit."""

from __future__ import annotations

from lxml import etree

from lc_translator.mapping import Camt087MappedLc

_NS = "urn:iso:std:iso:20022:tech:xsd:camt.087.001.05"
NSMAP = {" Document xmlns="""

from lxml import etree

from lc_translator.mapping import Camt087MappedLc

_NS = "urn:iso:std:iso:20022:tech:xsd:camt.087.001.05"
NSMAP = {"camt": _NS}


def _q(tag: str) -> str:
    return f"{{{_NS}}}{tag}"


class Camt087Generator:
    """Build a camt.087.001.05 XML document from mapped LC data."""

    def generate(self, mapped: Camt087MappedLc) -> str:
        """Return a UTF-8 encoded XML string."""
        root = etree.Element(_q("Document"), nsmap={None: _NS})
        payment = etree.SubElement(root, _q("PmtRtr"))

        grp_hdr = etree.SubElement(payment, _q("GrpHdr"))
        msg_id = etree.SubElement(grp_hdr, _q("MsgId"))
        msg_id.text = mapped.credit_id
        cre_dt_tm = etree.SubElement(grp_hdr, _q("CreDtTm"))
        cre_dt_tm.text = mapped.creation_datetime.isoformat()

        tx = etree.SubElement(payment, _q("TxInf"))
        rtr_id = etree.SubElement(tx, _q("RtrId"))
        rtr_id.text = mapped.credit_id

        instd_amt = etree.SubElement(tx, _q("InstdAmt"))
        instd_amt.set("Ccy", mapped.instructed_currency)
        instd_amt.text = str(mapped.instructed_amount)

        dbtr = etree.SubElement(tx, _q("Dbtr"))
        dbtr_pty = etree.SubElement(dbtr, _q("Pty"))
        dbtr_nm = etree.SubElement(dbtr_pty, _q("Nm"))
        dbtr_nm.text = mapped.debtor_name
        dbtr_adr = etree.SubElement(dbtr_pty, _q("PstlAdr"))
        dbtr_adr.text = mapped.debtor_address

        cdtr = etree.SubElement(tx, _q("Cdtr"))
        cdtr_pty = etree.SubElement(cdtr, _q("Pty"))
        cdtr_nm = etree.SubElement(cdtr_pty, _q("Nm"))
        cdtr_nm.text = mapped.creditor_name
        cdtr_adr = etree.SubElement(cdtr_pty, _q("PstlAdr"))
        cdtr_adr.text = mapped.creditor_address

        return etree.tostring(root, pretty_print=True, xml_declaration=True, encoding="UTF-8").decode("utf-8")
```

**Step 2:** Create tests.

```python
"""Tests for camt.087 XML generation."""

from datetime import date, datetime
from decimal import Decimal

from lc_translator.mapping import Camt087MappedLc
from lc_translator.mx import Camt087Generator


def test_generate_includes_amount_and_parties() -> None:
    mapped = Camt087MappedLc(
        credit_id="LC001",
        creation_datetime=datetime(2026, 1, 15),
        expiry_date="2026-04-15",
        expiry_place="Rotterdam",
        instructed_amount=Decimal("10000.00"),
        instructed_currency="EUR",
        debtor_name="Acme",
        debtor_address="NYC",
        creditor_name="Global",
        creditor_address="Rotterdam",
    )
    xml = Camt087Generator().generate(mapped)
    assert 'Ccy="EUR"' in xml
    assert "10000.00" in xml
    assert "Acme" in xml
    assert "Global" in xml
```

**Step 3: Verify**

Run:
```bash
uv run pytest tests/unit/test_mx.py -v
```

Expected: 1 test passing.

**Step 4: Commit**

```bash
git add src/lc_translator/mx.py tests/unit/test_mx.py
git commit -m "feat: add camt.087 MX XML generator"
```


### Task 11: Implement XSD validation and schema acquisition

**Files:**
- Create: `src/lc_translator/validation.py`
- Create: `scripts/fetch_xsd.py`
- Create: `tests/unit/test_validation.py`

**Step 1:** Implement validation module.

```python
"""XSD loading, caching, and XML validation."""

from __future__ import annotations

import os
from pathlib import Path

from lxml import etree

from lc_translator.exceptions import XsdValidationError

_DEFAULT_CACHE_DIR = Path.home() / ".cache" / "lc-translator" / "xsd"


def _xsd_path_from_env() -> Path | None:
    env = os.environ.get("LC_TRANSLATOR_XSD_PATH")
    return Path(env) if env else None


def _camt087_builtin_path() -> Path | None:
    here = Path(__file__).resolve().parent
    candidate = here / "schemas" / "camt.087.001.05.xsd"
    return candidate if candidate.exists() else None


def _find_xsd_path() -> Path | None:
    return _xsd_path_from_env() or _camt087_builtin_path()


class XsdValidator:
    """Validate camt.087 XML against its XSD schema."""

    def __init__(self, xsd_path: Path | None = None) -> None:
        """Initialize validator.

        If xsd_path is provided, it is used directly. Otherwise the validator
        looks at LC_TRANSLATOR_XSD_PATH, then the built-in schema directory.
        """
        self.xsd_path = xsd_path or _find_xsd_path()
        self._schema: etree.XMLSchema | None = None

    def is_available(self) -> bool:
        """Return True if an XSD schema file was located."""
        return self.xsd_path is not None

    def _load_schema(self) -> etree.XMLSchema:
        if self._schema is None:
            if self.xsd_path is None or not self.xsd_path.exists():
                raise XsdValidationError("XSD schema not found")
            tree = etree.parse(str(self.xsd_path))
            self._schema = etree.XMLSchema(tree)
        return self._schema

    def validate(self, xml_text: str) -> None:
        """Validate XML text against the XSD."""
        schema = self._load_schema()
        try:
            root = etree.fromstring(xml_text.encode("utf-8"))
            schema.assertValid(root)
        except etree.DocumentInvalid as exc:
            raise XsdValidationError(f"XSD validation failed: {exc}") from exc
        except etree.XMLSyntaxError as exc:
            raise XsdValidationError(f"Malformed XML: {exc}") from exc
```

**Step 2:** Implement XSD fetch script.

```python
"""Download the official camt.087 XSD to the local cache."""

from __future__ import annotations

import urllib.request
from pathlib import Path

_SCHEMA_URL = "https://www.iso20022.org/sites/default/files/media/file/camt.087.001.05.xsd"
_CACHE_DIR = Path.home() / ".cache" / "lc-translator" / "xsd"


def main() -> None:
    """Download the camt.087 XSD if available."""
    _CACHE_DIR.mkdir(parents=True, exist_ok=True)
    destination = _CACHE_DIR / "camt.087.001.05.xsd"
    print(f"Downloading {_SCHEMA_URL} ...")
    try:
        urllib.request.urlretrieve(_SCHEMA_URL, destination)
        print(f"Saved to {destination}")
    except Exception as exc:  # noqa: BLE001
        print(f"Failed to download schema: {exc}")
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
```

**Step 3:** Create tests.

```python
"""Tests for XSD validation."""

from datetime import datetime
from decimal import Decimal

import pytest

from lc_translator.exceptions import XsdValidationError
from lc_translator.mapping import Camt087MappedLc
from lc_translator.mx import Camt087Generator
from lc_translator.validation import XsdValidator


def test_validator_unavailable_when_no_schema() -> None:
    validator = XsdValidator(xsd_path=Path("/does/not/exist.xsd"))
    assert not validator.is_available()


def test_validate_raises_without_schema() -> None:
    validator = XsdValidator(xsd_path=Path("/does/not/exist.xsd"))
    xml = Camt087Generator().generate(
        Camt087MappedLc(
            credit_id="LC001",
            creation_datetime=datetime(2026, 1, 15),
            expiry_date="2026-04-15",
            expiry_place="Rotterdam",
            instructed_amount=Decimal("10000.00"),
            instructed_currency="EUR",
            debtor_name="Acme",
            debtor_address="NYC",
            creditor_name="Global",
            creditor_address="Rotterdam",
        )
    )
    with pytest.raises(XsdValidationError):
        validator.validate(xml)
```

**Step 4: Verify**

Run:
```bash
uv run pytest tests/unit/test_validation.py -v
```

Expected: 2 tests passing.

**Step 5: Commit**

```bash
git add src/lc_translator/validation.py scripts/fetch_xsd.py tests/unit/test_validation.py
git commit -m "feat: add XSD validator and schema fetch script"
```


### Task 12: Build the CLI

**Files:**
- Create: `src/lc_translator/cli.py`
- Create: `tests/integration/test_pipeline.py`

**Step 1:** Implement CLI.

```python
"""Command-line interface for lc-translator."""

from __future__ import annotations

from pathlib import Path

import typer

from lc_translator import __version__
from lc_translator.generator import generate_lc
from lc_translator.mapping import map_lc_to_camt087
from lc_translator.mt700 import Mt700Parser, Mt700Serializer, Mt700Validator
from lc_translator.mx import Camt087Generator
from lc_translator.validation import XsdValidator

app = typer.Typer(help="MT700 to camt.087 Letter of Credit translator")


@app.command()
def generate(
    seed: int | None = typer.Option(None, "--seed", help="Random seed for reproducible output"),
    strict: bool = typer.Option(False, "--strict", help="Fail on parser warnings"),
) -> None:
    """Generate an LC, emit MT700 and MX XML, and validate."""
    lc = generate_lc(seed=seed)
    mt_text = Mt700Serializer().serialize(lc)
    validator = Mt700Validator()
    mt_report = validator.validate(mt_text)

    parse_result = Mt700Parser().parse(mt_text)
    if strict and (parse_result.errors or parse_result.warnings):
        raise typer.BadParameter(f"Strict parse failures: {parse_result.errors + parse_result.warnings}")
    if not parse_result.ok():
        typer.secho(f"Parse errors: {parse_result.errors}", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    mapped = map_lc_to_camt087(parse_result.lc)  # type: ignore[arg-type]
    xml = Camt087Generator().generate(mapped)

    xsd_validator = XsdValidator()
    if xsd_validator.is_available():
        xsd_validator.validate(xml)
        typer.secho("XSD validation: PASSED", fg=typer.colors.GREEN)
    else:
        typer.secho("XSD validation: SKIPPED (no schema found)", fg=typer.colors.YELLOW)

    typer.echo("--- MT700 ---")
    typer.echo(mt_text)
    typer.echo("\n--- MT700 validation ---")
    typer.echo(f"Valid: {mt_report.valid}")
    if mt_report.warnings:
        typer.echo(f"Warnings: {mt_report.warnings}")
    if mt_report.errors:
        typer.echo(f"Errors: {mt_report.errors}")

    typer.echo("\n--- MX (camt.087) ---")
    typer.echo(xml)


@app.command()
def mt_to_mx(
    file: Path = typer.Argument(..., help="Path to MT700 text file", exists=True),
) -> None:
    """Read MT700 from file, translate to MX XML, and print."""
    mt_text = file.read_text()
    result = Mt700Parser().parse(mt_text)
    if not result.ok():
        typer.secho(f"Parse failed: {result.errors}", fg=typer.colors.RED)
        raise typer.Exit(code=1)
    mapped = map_lc_to_camt087(result.lc)  # type: ignore[arg-type]
    xml = Camt087Generator().generate(mapped)
    typer.echo(xml)


@app.command()
def validate_mt(
    file: Path = typer.Argument(..., help="Path to MT700 text file", exists=True),
) -> None:
    """Validate MT700 structure."""
    mt_text = file.read_text()
    report = Mt700Validator().validate(mt_text)
    if report.valid:
        typer.secho("MT700 structure: VALID", fg=typer.colors.GREEN)
    else:
        typer.secho("MT700 structure: INVALID", fg=typer.colors.RED)
        for err in report.errors:
            typer.echo(f"  ERROR: {err}")
        raise typer.Exit(code=1)


@app.command()
def validate_mx(
    file: Path = typer.Argument(..., help="Path to MX XML file", exists=True),
    xsd_path: Path | None = typer.Option(None, "--xsd", help="Path to camt.087 XSD"),
) -> None:
    """Validate MX XML against the camt.087 XSD."""
    xml_text = file.read_text()
    validator = XsdValidator(xsd_path=xsd_path)
    if not validator.is_available():
        typer.secho("No XSD schema available. Set LC_TRANSLATOR_XSD_PATH or run scripts/fetch_xsd.py", fg=typer.colors.YELLOW)
        raise typer.Exit(code=1)
    validator.validate(xml_text)
    typer.secho("MX XSD validation: PASSED", fg=typer.colors.GREEN)


@app.command()
def version() -> None:
    """Print version."""
    typer.echo(__version__)
```

**Step 2:** Create integration test.

```python
"""End-to-end pipeline integration test."""

from lc_translator.generator import generate_lc
from lc_translator.mapping import map_lc_to_camt087
from lc_translator.mt700 import Mt700Parser, Mt700Serializer, Mt700Validator
from lc_translator.mx import Camt087Generator


def test_full_pipeline_with_deterministic_seed() -> None:
    lc = generate_lc(seed=42)
    mt_text = Mt700Serializer().serialize(lc)

    mt_report = Mt700Validator().validate(mt_text)
    assert mt_report.valid, mt_report.errors

    parse_result = Mt700Parser().parse(mt_text)
    assert parse_result.ok(), parse_result.errors

    mapped = map_lc_to_camt087(parse_result.lc)  # type: ignore[arg-type]
    xml = Camt087Generator().generate(mapped)
    assert "InstdAmt" in xml
    assert lc.lc_number in xml
```

**Step 3: Verify**

Run:
```bash
uv run pytest tests/integration/test_pipeline.py -v
uv run lc-translator generate --seed 42
```

Expected: integration test passes and CLI prints MT700 then MX XML.

**Step 4: Commit**

```bash
git add src/lc_translator/cli.py tests/integration/test_pipeline.py
git commit -m "feat: add typer CLI and end-to-end pipeline test"
```


### Task 13: Add README and final polish

**Files:**
- Create: `README.md`
- Modify: `src/lc_translator/__init__.py` if needed

**Step 1:** Write README.

```markdown
# lc-translator

A demonstration Python CLI that translates a Letter of Credit from the legacy SWIFT MT700 format to the ISO 20022 `camt.087` XML format.

## Why

Banks and trade platforms are migrating from SWIFT MT messages to ISO 20022 MX messages. This project shows both formats side by side and proves the translation pipeline with validation.

## Quick Start

```bash
uv sync --extra dev
uv run lc-translator generate --seed 42
```

## Pipeline

1. **Generate** a realistic `LetterOfCredit` using Faker.
2. **Serialize** it to SWIFT MT700 text.
3. **Parse** the MT700 back into the agnostic LC model.
4. **Map** the LC fields to camt.087 data structures.
5. **Generate** ISO 20022 XML.
6. **Validate** the MT700 structure and the MX XML against XSD.

## Commands

- `lc-translator generate [--seed N]` — run the full pipeline
- `lc-translator mt-to-mx <mt700.txt>` — translate a file
- `lc-translator validate-mt <mt700.txt>` — check MT700 structure
- `lc-translator validate-mx <mx.xml> --xsd <camt.087.xsd>` — validate MX XML
- `lc-translator version` — print version

## XSD Schema

Download the official schema:

```bash
uv run python scripts/fetch_xsd.py
export LC_TRANSLATOR_XSD_PATH="$HOME/.cache/lc-translator/xsd/camt.087.001.05.xsd"
```

## Development

```bash
uv run pytest
uv run ruff check --fix .
uv run ruff format .
uv run mypy src tests
```

## Domain Notes

- **MT700** ("Issue of a Documentary Credit") uses block-text tags like `:20:`, `:31C:`, `:50:`, `:59:`, `:32B:`.
- **camt.087** expresses the same trade party and amount data as XML nodes such as `<InstdAmt>`, `<Dbtr>`, and `<Cdtr>`.
```

**Step 2: Verify**

Run:
```bash
uv run pytest
uv run ruff check src tests
uv run mypy src tests
```

Expected: all tests pass, no lint errors, no mypy errors (or only safe ignores).

**Step 3: Commit**

```bash
git add README.md
git commit -m "docs: add README with quick start and domain notes"
```


## Verification Summary

After all tasks complete:

- [ ] All tests pass: `uv run pytest`
- [ ] CLI runs end-to-end: `uv run lc-translator generate --seed 42`
- [ ] Linting passes: `uv run ruff check src tests`
- [ ] Formatting passes: `uv run ruff format --check src tests`
- [ ] Type checking passes: `uv run mypy src tests`
- [ ] MT700 validator catches missing tags and long lines.
- [ ] XSD validation works when schema is available via `LC_TRANSLATOR_XSD_PATH` or downloaded with `scripts/fetch_xsd.py`.
