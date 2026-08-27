# lc-translator

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)]()
[![React](https://img.shields.io/badge/React-20232A?logo=react&logoColor=61DAFB)]()

I had a meeting with a trade finance company that specializes in managing trade documents, and wanted to learn more about their stack and demonstrate a way to use AI enablement to investigate a simple feature. Lately, I have been using node and typescript and react, so, I wanted to use some of their stack choices: python, javascript, and react. It uses a monorepo-style setup with `uv` and `pnpm`.

This is a hands-on demonstration of bridging legacy trade-finance messaging to modern ISO 20022 XML. It takes a SWIFT MT700 documentary credit, parses it into an agnostic domain model, and emits a validated ISO 20022 `tsrv.001` (Undertaking Issuance) XML document.

This is intentionally demo-grade code: it shows a clean vertical slice of a financial message-transformation pipeline using a `uv` + `pnpm` monorepo, Pydantic modeling, explicit field mapping, and real XSD validation.

![LC Translator Generate page](screenshot.png)

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

### Example

Given an MT700 fragment like:

```text
:20:LC123456789
:31C:260101
:31D:260615
:50:Acme Exporters Inc.
:59:Global Importers Ltd
:32B:USD100000,
```

The pipeline maps it into `tsrv.001.001.01` XML containing `<UdrtkgIssnc>`, `<Issr>`, `<Bnfcry>`, and `<UdrtkgAmt Ccy="USD">100000</UdrtkgAmt>`, then validates it against the bundled XSD.

## Architecture

```
lc-translator/
├── packages/
│   ├── lc-translator-core/     # reusable engine + CLI
│   └── lc-translator-api/      # FastAPI REST service
├── apps/
│   └── web/                    # React 19 + Vite + Tailwind
├── pyproject.toml              # uv workspace root
├── pnpm-workspace.yaml         # pnpm workspace root
├── package.json                # shared JS scripts
├── docker-compose.yml          # optional one-command demo
└── scripts/run-dev.sh          # unified dev startup
```

## Prerequisites

- Python 3.9+
- [uv](https://docs.astral.sh/uv/)
- Node.js 20+
- [pnpm](https://pnpm.io/)

## Quick start

```bash
uv sync --extra dev
pnpm install
uv run lc-translator generate --seed 42
```

No PostgreSQL is required for the quick start above — the core pipeline and CLI run entirely in-process.

## Environment variables

| Variable | Default | Purpose |
|---|---|---|
| `LC_TRANSLATOR_DATABASE_URL` | `postgresql+psycopg://postgres:postgres@localhost:5432/lc_translator` | PostgreSQL connection string. Only needed for the Records API. |
| `LC_TRANSLATOR_XSD_PATH` | bundled `tsrv.001.001.01.xsd` | Path to an alternative ISO 20022 XSD file. |
| `LC_TRANSLATOR_STATIC_DIR` | none | Directory to serve the built React UI from the API container. |
| `LC_TRANSLATOR_CORS_ORIGINS` | `http://localhost:5173` | Allowed CORS origins for the API. |

## Development

### Start the API server

```bash
pnpm run dev:api
# or directly
uv run --package lc-translator-api uvicorn lc_translator_api.main:app --reload
```

### Start the React dev server

```bash
pnpm run dev:web
```

### Start both with one command

```bash
./scripts/run-dev.sh
```

The React dev server proxies `/api/*` to the FastAPI backend at `http://localhost:8000`.

### Serve the built frontend from the API

```bash
pnpm run build:web
LC_TRANSLATOR_STATIC_DIR=apps/web/dist uv run --package lc-translator-api uvicorn lc_translator_api.main:app
```

Then open http://localhost:8000.

## CLI commands (core package)

| Command | Purpose |
|---|---|
| `uv run lc-translator generate [--seed N] [--strict]` | Run the full pipeline end-to-end. |
| `uv run lc-translator mt-to-mx <mt700.txt>` | Read MT700 from file and emit MX XML. |
| `uv run lc-translator validate-mt <mt700.txt>` | Validate MT700 structure. |
| `uv run lc-translator validate-mx <mx.xml> --xsd <schema.xsd>` | Validate MX XML against tsrv.001 XSD. |
| `uv run lc-translator version` | Print package version. |

## API endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/health` | Health check (includes DB status) |
| `POST` | `/api/generate` | Generate LC and run full pipeline |
| `POST` | `/api/mt-to-mx` | Translate MT700 text to MX XML |
| `POST` | `/api/validate-mt` | Validate MT700 structure |
| `POST` | `/api/validate-mx` | Validate MX XML against XSD |
| `POST` | `/api/records` | Save a record |
| `GET` | `/api/records` | List saved records |
| `GET` | `/api/records/{id}` | Fetch a record |
| `PUT` | `/api/records/{id}` | Update record title |
| `DELETE` | `/api/records/{id}` | Delete a record |
| `POST` | `/api/records/{id}/rerun` | Re-run stored input |

## Web UI

The React app runs at `http://localhost:5173` in development. It has four views:

- **Generate** — generate a fake LC and view MT700 + MX output
- **Translate** — paste MT700 text and convert to MX XML
- **Validate** — validate MT700 structure or MX XML
- **Records** — saved translation/generation records with delete support

Recent results are stored in the browser's `localStorage` (up to 10 entries) so you can revisit them during the session.

## Docker Compose

Build and run the full stack in one command:

```bash
docker compose up --build
```

Then open http://localhost:8000.

This starts PostgreSQL, runs Alembic migrations automatically, and serves the built React UI from the FastAPI container.

## Storage

The Records API persists saved translations in PostgreSQL. If you only use the CLI or the Generate/Translate/Validate features, **you do not need a database**.

To run the full stack with records support, Docker Compose is the fastest path. For local development with your own Postgres:

```bash
export LC_TRANSLATOR_DATABASE_URL=postgresql+psycopg://user:pass@localhost:5432/lc_translator
uv run --package lc-translator-api alembic upgrade head
```

## Testing

```bash
# Python tests
uv run pytest

# React tests
pnpm --filter web test

# All web tests from root
pnpm run test:web

# Run everything
uv run pytest && pnpm run test:web
```

## Linting and formatting

```bash
uv run ruff check packages
uv run ruff format packages
uv run mypy packages
```

## XSD schema

The project bundles the official ISO 20022 schema at `packages/lc-translator-core/src/lc_translator_core/schemas/tsrv.001.001.01.xsd`. The CLI and API use it automatically, so XSD validation works out of the box.

To use a different copy of the schema, set `LC_TRANSLATOR_XSD_PATH`:

```bash
export LC_TRANSLATOR_XSD_PATH=/path/to/tsrv.001.001.01.xsd
uv run lc-translator generate --seed 42
```

## Business domain

- **MT700** — SWIFT "Issue of a Documentary Credit". Block-text tags such as `:20:`, `:31C:`, `:31D:`, `:50:`, `:59:`, and `:32B:` carry the LC data.
- **tsrv.001** — ISO 20022 Trade Services message for **Undertaking Issuance**. In this demo, MT700 fields are mapped into the official `tsrv.001.001.01` structure (`UdrtkgIssnc`, `Issr`, `Bnfcry`, `UdrtkgAmt`, etc.). A traditional commercial LC would map into the broader ISO 20022 Trade Services family; `tsrv.001` is the closest undertaking-issuance message available in a downloadable public archive.

## Notes

- Target Python version is **3.9+** so it runs on stock macOS Python.
- The parser is best-effort: it recovers whatever it can and reports what it could not.
- The bundled XSD is the official `tsrv.001.001.01` schema from the ISO 20022 Trade Services business area archive. It validates the generated XML against the real global standard.

## License

This project is released under the [MIT License](LICENSE).
