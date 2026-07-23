title: MT-to-MX Letter of Credit Translation Engine — Technical Design
tags:
  - design
  - mt-to-mx-lc-engine
  - fintech
  - swift
  - iso-20022
keywords:
  - SWIFT MT700
  - ISO 20022 camt.087
  - Letter of Credit
  - trade finance
  - MT-to-MX translation
  - XSD validation
  - Pydantic
  - lxml
  - typer
  - uv
distilled: 2026-07-23

# MT-to-MX Letter of Credit Translation Engine — Technical Design

## Architecture Overview

The application is a vertical slice through a message-translation pipeline. It is organized as a pure-Python library with a thin CLI on top. There is no persistence layer, no network service, and no UI. The pipeline is:

```
Agnostic LC model → MT700 text → Agnostic LC model → camt.087 XML → validation
```

The same `LetterOfCredit` model is used at both ends, proving that the translation is reversible in spirit: MT700 and MX are two serializations of the same trade facts.

Code is organized by architectural layer under `src/lc_translator/`:

- `models/` — domain types (`LetterOfCredit`, parties, addresses, money).
- `generator/` — fake trade data generator built on `Faker`.
- `mt700/` — serializer and parser for SWIFT MT700 messages, plus a lightweight validator.
- `mapping/` — explicit dictionary/functions mapping MT700 tags to `camt.087` nodes.
- `mx/` — `camt.087` XML generator.
- `validation/` — XSD loading/validation and schema acquisition helpers.
- `cli/` — `typer` commands.
- `exceptions/` — custom exceptions and result types for best-effort parsing.

Tests live outside the package in `tests/`, mirroring the package layout.

## Components

### 1. Data model (`lc_translator.models`)

`LetterOfCredit` is a Pydantic v2 `BaseModel` with nested types:

- `Party` (applicant/beneficiary bank) with `name`, `address`, and optional `bic`.
- `Money` with `currency: str` (ISO 4217) and `amount: Decimal`.
- `Port` with `name` and optional `country`.
- Dates use `datetime.date`.

Pydantic gives us validation, coercion, serialization, and clear error messages out of the box.

### 2. Fake generator (`lc_translator.generator`)

`generate_lc()` returns a random `LetterOfCredit`. Uses `Faker` for:

- Corporate names and addresses.
- 8/11-character SWIFT/BIC codes.
- ISO currency codes USD/EUR/GBP.
- High-value `Decimal` amounts.
- Realistic port names.
- Issue date today, expiry date 30-180 days in the future.

A deterministic seed mode is supported for reproducible demos and tests.

### 3. MT700 serializer (`lc_translator.mt700.serializer`)

`Mt700Serializer.serialize(lc: LetterOfCredit) -> str`

- Maps fields to tags `:20:`, `:31C:`, `:31D:`, `:50:`, `:59:`, `:32B:`, plus optional banks (`:40A:`, `:57D:` etc. as needed).
- Enforces SWIFT line-length rules (e.g., 65 chars per line for most tags, 35 for addresses).
- Uses CRLF line endings per SWIFT convention.
- Returns the raw block-text MT700 string.

### 4. MT700 parser (`lc_translator.mt700.parser`)

`Mt700Parser.parse(text: str) -> ParseResult`

- Best-effort recovery. Parses whatever is present, records warnings for missing/ malformed tags.
- Returns `ParseResult(lc=LetterOfCredit | None, warnings=list[str], errors=list[str])`.
- Robust to missing optional tags and extra blank lines.
- Reports to the user what was recovered and what was skipped/fixed.

### 5. Mapping layer (`lc_translator.mapping`)

`translate(lc: LetterOfCredit) -> camt087.CreditTransferTransaction` (or equivalent container)

- Explicit mapping functions, not magic reflection.
- The mapping documents the business correspondence between old and new formats, which is valuable for learning the domain.

Example mapping:

| MT700 tag | camt.087 node |
|---|---|
| `:20:` | `Undrlyg/LclInstrm/Cd` |
| `:31C:` | `CreDtTm` |
| `:31D:` | `XpryDt` + `XpryPlc` |
| `:50:` | `Dbtr/Pty/Nm` + `Dbtr/Pty/PstlAdr` |
| `:59:` | `Cdtr/Pty/Nm` + `Cdtr/Pty/PstlAdr` |
| `:32B:` | `InstdAmt` with `Ccy` attribute |

### 6. MX generator (`lc_translator.mx`)

`Camt087Generator.generate(lc: LetterOfCredit) -> str`

- Builds XML with `lxml.etree` for namespaces and pretty printing.
- Produces a `Document` root with the correct `camt.087.001.xxx` namespace.
- Validates the generated tree against the loaded XSD before returning (or raises a validation error with details).

### 7. Validation layer (`lc_translator.validation`)

Two responsibilities:

1. **MT700 structure validation** — tag presence, line lengths, required fields. Returns a structured report.
2. **MX XSD validation** — load `camt.087` XSD via `lxml.etree.XMLSchema`, validate XML, and report errors.

**Schema acquisition strategy (option C):**

- At runtime, try to resolve a local schema file pointed to by `LC_TRANSLATOR_XSD_PATH`.
- If absent, attempt to download the official schema from ISO 20022/SWIFT into a cache directory (`~/.cache/lc-translator/xsd/`).
- If both fail, log a clear error and skip XSD validation while still emitting the XML.
- A script `scripts/fetch_xsd.py` is provided to pre-download the schema for offline demos.
- The bundled schema (if redistributable) ships under `lc_translator/schemas/`.

### 8. CLI (`lc_translator.cli`)

`typer` commands:

- `lc-translator generate` — create an LC, print MT700, print MX XML, and run validation.
- `lc-translator mt-to-mx <file>` — read MT700 from file, translate to MX, validate.
- `lc-translator validate-mt <file>` — validate MT700 structure.
- `lc-translator validate-mx <file>` — validate MX XML against XSD.
- `--seed` for reproducible generation.
- `--strict` to fail on parser warnings.

### 9. Exceptions (`lc_translator.exceptions`)

- `LcTranslatorError` — base exception.
- `Mt700FormatError` — invalid MT700 structure.
- `XsdValidationError` — MX XML failed XSD validation.
- `ParseResult` dataclass for best-effort recovery (not an exception, but lives here).

## Data Flow

A single user command such as `lc-translator generate --seed 42` flows through the system as follows:

1. CLI parses args and calls `generator.generate_lc(seed=42)`.
2. Generator returns a `LetterOfCredit` model.
3. CLI calls `mt700.Mt700Serializer.serialize(lc)`, producing an MT700 string.
4. CLI optionally calls `mt700.Mt700Validator.validate(mt_text)` to check structure.
5. CLI calls `mt700.Mt700Parser.parse(mt_text)`, receiving `ParseResult`.
6. If parsing succeeded, CLI calls `mapping.translate(parse_result.lc)` to build a `camt.087` data representation.
7. CLI calls `mx.Camt087Generator.generate(...)` to emit XML.
8. XML is validated against the XSD via `validation.XsdValidator`.
9. CLI prints MT700, MX XML, and any warnings/validation messages to stdout.

## Key Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Language / target | Python 3.9+ | Matches the available environment; broad bank/fintech compatibility. |
| Data model | Pydantic v2 | Validation, clear errors, and fast Rust-backed core. |
| XML handling | `lxml` | Mature, C-backed, supports full XSD validation and namespaces. |
| CLI | `typer` | Type-driven, modern, good `--help` output for demos. |
| Package/venv | `uv` | Rust-backed, fast, modern replacement for pip/venv/pip-tools. |
| Format/lint | `ruff` | Rust-backed, replaces many tools. |
| Type checking | `mypy` strict | Catches domain/model errors early. |
| Tests | `pytest` + `pytest-cov` + optional `freezegun` | Standard, well-documented, easy for a Python newcomer. |
| Parser behavior | Best-effort recovery with feedback | Matches real-world integrations; teaches user what changed. |
| XSD sourcing | Bundled + optional download | Maximizes chance of running a real validation without blocking first use. |
| Project layout | `src/` layout with separate `tests/` | Clean separation; follows modern Python packaging conventions. |

## Error Handling

- **Input boundaries:** Pydantic validates the `LetterOfCredit` model at creation. Conversion failures raise `ValueError` with context.
- **MT700 serializer:** Raises `Mt700FormatError` if the model cannot be represented within SWIFT rules.
- **MT700 parser:** Never raises on malformed input unless `--strict` is set. Always returns a `ParseResult` with `errors` and `warnings`.
- **XML generator:** Raises `LcTranslatorError` if required mapping data is missing.
- **XSD validation:** Raises `XsdValidationError` with line/column and schema error message on failure.
- **Schema acquisition:** Logs warnings if the schema cannot be found/downloaded; does not crash the generate command.

## Testing Approach

- **Unit tests** for each component in isolation (`tests/unit/`).
- **Integration tests** for the full pipeline (`tests/integration/test_pipeline.py`).
- **Snapshot/golden tests** for MT700 output and MX XML to detect regressions.
- **Validation tests** with a known-good and known-bad XSD path.
- Test fixtures in `tests/conftest.py` provide a deterministic `LetterOfCredit` instance.
- Aim for high coverage of the mapping and validation layers.

## Project Layout

```
lc_translator/
├── pyproject.toml
├── README.md
├── uv.lock
├── scripts/
│   └── fetch_xsd.py
├── schemas/
│   └── (official or representative camt.087 XSD)
├── src/
│   └── lc_translator/
│       ├── __init__.py
│       ├── cli.py
│       ├── __version__.py
│       ├── exceptions.py
│       ├── generator.py
│       ├── mapping.py
│       ├── models.py
│       ├── mx.py
│       ├── validation.py
│       └── mt700/
│           ├── __init__.py
│           ├── parser.py
│           ├── serializer.py
│           └── validator.py
└── tests/
    ├── conftest.py
    ├── unit/
    │   ├── test_models.py
    │   ├── test_generator.py
    │   ├── test_mt700.py
    │   ├── test_mapping.py
    │   └── test_mx.py
    └── integration/
        └── test_pipeline.py
```

## Open Items to Resolve in Planning

1. Exact official XSD URL/path and redistribution terms.
2. How many optional MT700 tags to include in v1 (minimal vs. representative).
3. Whether to add an integration test that downloads the XSD live in CI.
