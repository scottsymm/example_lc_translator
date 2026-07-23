title: MT-to-MX Letter of Credit Translation Engine — Spec
tags:
  - spec
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
  - SWIFT message migration
  - XSD validation
distilled: 2026-07-23

# MT-to-MX Letter of Credit Translation Engine — Spec

## Problem Statement

Global banks and trade platforms are migrating from legacy SWIFT MT messages to ISO 20022 MX messages. For a new engineer at Trade Technologies, understanding both formats and how data maps from one to the other is essential domain knowledge. There is no internal, runnable example that generates both the old (MT700) and new (`camt.087`) forms of a Letter of Credit and proves they represent the same trade.

## Target Audience

Primary: senior developers and the CTO evaluating the project as a technical demonstration and learning artifact.

Secondary: the engineer building it, as an on-ramp to the trade-finance domain.

## Core Value Proposition

A single, clean Python CLI that:
1. Generates realistic LC data.
2. Produces a valid SWIFT MT700 message.
3. Parses the MT700 and translates it into a valid ISO 20022 `camt.087` XML document.
4. Validates both the MT700 structure and the MX XML against the official XSD.

The project also teaches the domain: what an LC is, which MT tags carry which data, and how ISO 20022 represents the same trade.

## MVP Scope

### Included
- `LetterOfCredit` agnostic data model with fields for LC number, issue/expiry dates, applicant, beneficiary, issuing/advising banks, currency, amount, and port of loading.
- Fake generator using `Faker` for corporate names, addresses, SWIFT/BIC codes, ports, currency, and high-value amounts.
- MT700 serializer that enforces tag structure and line-length rules.
- MT700 parser to recover the agnostic model from a serialized MT700 string.
- MT700-to-MX mapping function/dictionary defining how legacy tags map to `camt.087` nodes.
- MX (`camt.087`) generator producing well-formed XML.
- Validation layer:
  - Internal MT700 structure validation.
  - XSD validation of the MX output against `camt.087.xsd`.
- CLI script that executes the full pipeline: generate → MT700 → parse → MX → validate.
- README with domain overview, architecture, run instructions, and references.

### Excluded from v1
- Any web UI or React frontend.
- Full SWIFT MT700 tag coverage (v1 focuses on the core tags listed in the plan).
- Network integration or real SWIFT message exchange.
- Persistence/database layer.

## Success Metrics

- The CLI runs end-to-end without errors.
- Generated MT700 passes internal structure checks.
- Generated MX XML passes XSD validation.
- A reviewer can read the README and understand the business mapping from MT to MX.

## Key Risks & Open Questions

- **XSD availability:** The official `camt.087` XSD may require a login or specific license. A fallback or representative schema may be needed for offline validation.
- **Domain accuracy:** The mapping between MT700 tags and `camt.087` nodes must be credible to a trade-finance audience. Needs domain review or authoritative source.
- **Scope creep:** Adding a React UI or too many MT tags early could delay the demo. Keep v1 CLI-only and focused.
