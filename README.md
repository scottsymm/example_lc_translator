# lc-translator

A demonstration Python CLI that translates a Letter of Credit (LC) from the legacy SWIFT MT700 format to the ISO 20022 `tsrv.001` (Undertaking Issuance) XML format.

This project is built for senior-developer and CTO-level demos. It showcases a clean Python package structure, Pydantic domain modeling, best-effort parsing, explicit MT-to-MX mapping, and XSD validation against a real ISO 20022 schema.

## What it does

The pipeline is intentionally small and vertical:

```
Agnostic LC model → MT700 text → Agnostic LC model → tsrv.001 XML → validation
```

1. **Generate** a realistic `LetterOfCredit` using `Faker`.
2. **Serialize** it to a strict SWIFT MT700 message.
3. **Parse** the MT700 back into the agnostic LC model with warnings and errors.
4. **Map** LC fields to ISO 20022 `tsrv.001` nodes.
5. **Generate** the ISO 20022 XML document.
6. **Validate** the MT700 structure and the MX XML against the bundled official `tsrv.001` XSD.

## Business domain

- **MT700** — SWIFT "Issue of a Documentary Credit". Block-text tags such as `:20:`, `:31C:`, `:31D:`, `:50:`, `:59:`, and `:32B:` carry the LC data.
- **tsrv.001** — ISO 20022 Trade Services message for **Undertaking Issuance**. In this demo, MT700 fields are mapped into the official `tsrv.001.001.01` structure (`UdrtkgIssnc`, `Issr`, `Bnfcry`, `UdrtkgAmt`, etc.). A traditional commercial LC would map into the broader ISO 20022 Trade Services family; `tsrv.001` is the closest undertaking-issuance message available in a downloadable public archive.

## Quick start

```bash
uv sync --extra dev
uv run lc-translator generate --seed 42
```

## CLI commands

| Command | Purpose |
|---|---|
| `lc-translator generate [--seed N] [--strict]` | Run the full pipeline end-to-end. |
| `lc-translator mt-to-mx <mt700.txt>` | Read MT700 from file and emit MX XML. |
| `lc-translator validate-mt <mt700.txt>` | Validate MT700 structure. |
| `lc-translator validate-mx <mx.xml> --xsd <schema.xsd>` | Validate MX XML against tsrv.001 XSD. |
| `lc-translator version` | Print package version. |

## XSD schema

The project bundles the official ISO 20022 schema at `src/lc_translator/schemas/tsrv.001.001.01.xsd`. The CLI uses it automatically, so XSD validation works out of the box.

To use a different copy of the schema (e.g., a newer version from ISO 20022 / SWIFT), set `LC_TRANSLATOR_XSD_PATH` or pass `--xsd`:

```bash
uv run lc-translator generate --seed 42 --xsd /path/to/tsrv.001.001.01.xsd
```

The `scripts/fetch_xsd.py` helper can also download a schema URL. The ISO 20022 website may require a login, so the script is provided as a convenience:

```bash
uv run python scripts/fetch_xsd.py --url https://your-schema-host/tsrv.001.001.01.xsd
export LC_TRANSLATOR_XSD_PATH="$HOME/.cache/lc-translator/xsd/tsrv.001.001.01.xsd"
uv run lc-translator generate --seed 42
```

## Development

```bash
uv run pytest         # run tests with coverage
uv run ruff check src tests    # lint
uv run ruff format src tests   # format
uv run mypy src tests          # type check
```

### Troubleshooting

**`uv run pytest` fails with `error: Failed to spawn: pytest` / `No such file or directory`**

This happens when the virtual environment only has the runtime dependencies and not the dev extras. Run:

```bash
uv sync --extra dev
uv run pytest
```

You need `--extra dev` whenever you set up the project fresh, move the directory, or if `uv` automatically syncs without it.

## Project layout

```
lc_translator/
├── src/lc_translator/        # main package
│   ├── models.py             # Pydantic LC domain model
│   ├── generator.py          # fake data generator
│   ├── mapping.py            # MT700 → tsrv.001 mapping
│   ├── mx.py                 # tsrv.001 XML generator
│   ├── validation.py         # XSD loader / validator
│   ├── cli.py                # typer CLI
│   └── mt700/                # MT700 serializer/parser/validator
│   └── schemas/              # bundled ISO 20022 XSD
├── tests/                    # pytest suite
├── scripts/fetch_xsd.py      # schema downloader
└── pyproject.toml            # packaging and tool config
```

## Notes

- Target Python version is **3.9+** so it runs on stock macOS Python.
- The parser is best-effort: it recovers whatever it can and reports what it could not.
- The bundled XSD is the official `tsrv.001.001.01` schema from the ISO 20022 Trade Services business area archive. It validates the generated XML against the real global standard.
