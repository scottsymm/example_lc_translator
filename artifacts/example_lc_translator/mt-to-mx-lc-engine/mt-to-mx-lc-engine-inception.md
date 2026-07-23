title: MT-to-MX Letter of Credit Translation Engine
tags:
  - inception
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
incepted: 2026-07-23

# MT-to-MX Letter of Credit Translation Engine

## Idea

A command-line Python demonstration app that models a Letter of Credit as an agnostic data object, serializes it to the legacy SWIFT MT700 format, parses it back, and translates it into an ISO 20022 MX (camt.087) XML document. The project is designed for a new engineer joining Trade Technologies to learn trade-finance messaging while producing a credible technical demonstration for senior developers and the CTO.

## Goal

- **Success criteria**
  - Generate realistic LC trade data on demand using `Faker`.
  - Emit a strictly formatted SWIFT MT700 message with correct tags, line lengths, and required fields.
  - Parse the MT700 message and map its contents to ISO 20022 XML nodes.
  - Produce a valid `camt.087` MX XML document from the mapped data.
  - Validate the MT700 structure internally (tag presence, line limits, required fields).
  - Validate the MX output against the official ISO 20022 `camt.087` XSD.
  - Include clear project documentation that explains the business domain, the pipeline, and how SWIFT MT maps to ISO 20022 MX.

- **v1 feature list**
  - `LetterOfCredit` dataclass serving as the single source of truth for LC data.
  - Fake data generator for corporate parties, banks (BICs), currency/amount, ports, and dates.
  - MT700 serializer with tag-aware formatting and line-length enforcement.
  - MT700 parser that recovers the agnostic model from a raw MT700 string.
  - MT700-to-MX mapping layer translating legacy tags to `camt.087` XML elements.
  - MX (`camt.087`) XML generator implemented with `xml.etree.ElementTree` or `lxml`.
  - Validation layer: internal MT700 checks plus XSD validation of the MX output.
  - CLI entry point that runs the full pipeline end-to-end.
  - README with domain primer, architecture overview, and run instructions.

- **Open questions**
  - Source of the official `camt.087` XSD (ISO 20022 website, SWIFT MyStandards, or bundled simplified schema for offline use).
  - Whether to package the project with `uv`/`poetry` or a plain `requirements.txt` for the demo.

## Interview Results

**What is the actual problem you want to solve here, and who is this demonstration for?**
I am at a new company and want a code project that demonstrates generating the old and new way of using SWIFT Letter of Credit messages, and converting old to new.

**Who should be impressed or informed by the final deliverable?**
I will be demonstrating to senior developers and the CTO.

**Does the demo need to validate the output against a real ISO 20022 XSD, or is well-formed, representative XML enough?**
We definitely want validation.

**Should this be runnable as a single CLI/Bash command, or is it okay if the user runs a few Python scripts in sequence?**
I was thinking a Python application. If we need UI could React work?

**For the initial demo, I'd recommend a CLI-first Python application — it's what senior devs and a CTO will want to see first (clean architecture, tests, validation). A React UI can absolutely be added later as a second layer, but it shouldn't distract from the core translation engine in v1.**
Agreed.

**Which validation level is "must have" for v1?**
Agreed. C (both A and B).

## Timeline

- Incepted: 2026-07-23
- Target tech-incept and write-plan: within the next session
- v1 implementation target: TBD based on scheduling
