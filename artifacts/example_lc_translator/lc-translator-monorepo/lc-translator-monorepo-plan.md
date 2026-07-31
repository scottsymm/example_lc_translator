# LC Translator Monorepo — Web UI + REST API — Implementation Plan

*Created: 2026-07-31*

**Goal:** Refactor the existing `lc-translator` CLI demo into a `uv` + `pnpm` monorepo with a reusable Python core, a FastAPI REST service, and a React web UI.

**Architecture:**
- `packages/lc-translator-core/` — reusable LC engine (models, generator, MT700, MX, validation, CLI).
- `packages/lc-translator-api/` — FastAPI service exposing the engine over HTTP.
- `apps/web/` — React 19 + Vite + Tailwind CSS frontend.
- Root tooling — `uv` workspace for Python, `pnpm` workspace for JavaScript, optional Docker Compose.

**Tech Stack:**
- Python 3.9+, Pydantic v2, FastAPI, Uvicorn, Pydantic Settings, `uv` workspaces.
- React 19, Vite, Tailwind CSS, React Router, Vitest, React Testing Library, `pnpm` workspaces.

**Source:** `artifacts/example_lc_translator/lc-translator-monorepo/lc-translator-monorepo-discovery.md`


## File Map

### Monorepo root

| File | Action | Responsibility |
|---|---|---|
| `pyproject.toml` | Modify | uv workspace root; shared Python tooling config |
| `pnpm-workspace.yaml` | Create | pnpm workspace root |
| `package.json` | Create | root JS scripts and workspace declaration |
| `docker-compose.yml` | Create | optional one-command demo runner |
| `README.md` | Modify | updated monorepo overview and run instructions |

### Python core package

| File | Action | Responsibility |
|---|---|---|
| `packages/lc-translator-core/pyproject.toml` | Create | package metadata, dependencies, CLI script |
| `packages/lc-translator-core/src/lc_translator_core/__init__.py` | Create | public API exports |
| `packages/lc-translator-core/src/lc_translator_core/__version__.py` | Create/Migrate | single source of truth for version |
| `packages/lc-translator-core/src/lc_translator_core/models.py` | Migrate | existing Pydantic LC models |
| `packages/lc-translator-core/src/lc_translator_core/generator.py` | Migrate | Faker-based LC generator |
| `packages/lc-translator-core/src/lc_translator_core/mt700/` | Migrate | serializer, parser, validator |
| `packages/lc-translator-core/src/lc_translator_core/mapping.py` | Migrate | MT-to-MX mapping |
| `packages/lc-translator-core/src/lc_translator_core/mx.py` | Migrate | tsrv.001 XML generator |
| `packages/lc-translator-core/src/lc_translator_core/validation.py` | Migrate | XSD loading and validation |
| `packages/lc-translator-core/src/lc_translator_core/schemas/` | Migrate | bundled ISO 20022 XSD |
| `packages/lc-translator-core/src/lc_translator_core/cli.py` | Migrate | typer CLI entry point |
| `packages/lc-translator-core/tests/` | Migrate | existing core tests |
| `packages/lc-translator-core/scripts/fetch_xsd.py` | Migrate | schema downloader |

### FastAPI package

| File | Action | Responsibility |
|---|---|---|
| `packages/lc-translator-api/pyproject.toml` | Create | FastAPI package metadata and core dependency |
| `packages/lc-translator-api/src/lc_translator_api/__init__.py` | Create | package init |
| `packages/lc-translator-api/src/lc_translator_api/main.py` | Create | FastAPI app, lifespan, middleware, static mount |
| `packages/lc-translator-api/src/lc_translator_api/config.py` | Create | typed settings (CORS origins, static dir, xsd path) |
| `packages/lc-translator-api/src/lc_translator_api/dependencies.py` | Create | shared dependencies (settings, xsd schema) |
| `packages/lc-translator-api/src/lc_translator_api/routers/__init__.py` | Create | router aggregation |
| `packages/lc-translator-api/src/lc_translator_api/routers/generate.py` | Create | `/api/generate` endpoint |
| `packages/lc-translator-api/src/lc_translator_api/routers/translate.py` | Create | `/api/mt-to-mx` endpoint |
| `packages/lc-translator-api/src/lc_translator_api/routers/validate.py` | Create | `/api/validate-mt`, `/api/validate-mx`, `/api/health` endpoints |
| `packages/lc-translator-api/src/lc_translator_api/schemas/__init__.py` | Create | schema exports |
| `packages/lc-translator-api/src/lc_translator_api/schemas/generate.py` | Create | generate request/response models |
| `packages/lc-translator-api/src/lc_translator_api/schemas/translate.py` | Create | translate request/response models |
| `packages/lc-translator-api/src/lc_translator_api/schemas/validate.py` | Create | validate request/response models |
| `packages/lc-translator-api/tests/test_health.py` | Create | health endpoint test |
| `packages/lc-translator-api/tests/test_generate.py` | Create | generate endpoint test |
| `packages/lc-translator-api/tests/test_translate.py` | Create | mt-to-mx endpoint test |
| `packages/lc-translator-api/tests/test_validate.py` | Create | validate endpoints test |

### React web app

| File | Action | Responsibility |
|---|---|---|
| `apps/web/package.json` | Create | React app dependencies and scripts |
| `apps/web/vite.config.js` | Create | Vite configuration |
| `apps/web/tailwind.config.js` | Create | Tailwind configuration |
| `apps/web/postcss.config.js` | Create | PostCSS configuration |
| `apps/web/index.html` | Create | HTML entry point |
| `apps/web/src/main.jsx` | Create | React root render |
| `apps/web/src/App.jsx` | Create | top-level app with router |
| `apps/web/src/index.css` | Create | Tailwind directives + base styles |
| `apps/web/src/api/client.js` | Create | thin fetch wrapper for `/api/*` |
| `apps/web/src/lib/history.js` | Create | localStorage read/write for recent results |
| `apps/web/src/pages/GeneratePage.jsx` | Create | generate + display MT700/MX |
| `apps/web/src/pages/TranslatePage.jsx` | Create | paste MT700 + get MX |
| `apps/web/src/pages/ValidatePage.jsx` | Create | validate MT700 or MX |
| `apps/web/src/components/Header.jsx` | Create | navigation header |
| `apps/web/src/components/MessageBlock.jsx` | Create | read-only text display with copy button |
| `apps/web/src/components/HistoryPanel.jsx` | Create | collapsible panel of recent results |
| `apps/web/src/components/ValidationResult.jsx` | Create | display valid/errors/warnings |
| `apps/web/src/tests/setup.js` | Create | Vitest DOM setup |
| `apps/web/src/tests/GeneratePage.test.jsx` | Create | basic generate page test |
| `apps/web/src/tests/history.test.js` | Create | unit tests for localStorage history |


## Tasks

### Task 1: Bootstrap the monorepo workspace structure

**Files:**
- Modify: `pyproject.toml`
- Create: `pnpm-workspace.yaml`
- Create: `package.json`

**Step 1:** Rewrite root `pyproject.toml` as a uv workspace root.

```toml
[project]
name = "lc-translator-monorepo"
version = "0.2.0"
description = "Monorepo for the LC Translator engine, API, and web UI"
requires-python = ">=3.9"
readme = "README.md"
license = { text = "MIT" }

dependencies = []

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
    "ruff>=0.1.0",
    "mypy>=1.0",
]

[tool.uv.workspace]
members = ["packages/*"]

[tool.uv.sources]
lc-translator-core = { path = "packages/lc-translator-core" }
lc-translator-api = { path = "packages/lc-translator-api" }

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
testpaths = ["packages"]
python_files = ["test_*.py"]
addopts = "--cov=lc_translator_core --cov=lc_translator_api --cov-report=term-missing"
```

**Step 2:** Create `pnpm-workspace.yaml`.

```yaml
packages:
  - "apps/*"
```

**Step 3:** Create root `package.json`.

```json
{
  "name": "lc-translator-monorepo",
  "private": true,
  "version": "0.2.0",
  "type": "module",
  "scripts": {
    "dev:web": "pnpm --filter web dev",
    "dev:api": "uv run --package lc-translator-api uvicorn lc_translator_api.main:app --reload",
    "build:web": "pnpm --filter web build",
    "test:web": "pnpm --filter web test",
    "test:api": "uv run pytest packages/lc-translator-api/tests -v",
    "test:core": "uv run pytest packages/lc-translator-core/tests -v",
    "lint:web": "pnpm --filter web lint",
    "lint:api": "uv run ruff check packages/lc-translator-api/src packages/lc-translator-api/tests",
    "lint:core": "uv run ruff check packages/lc-translator-core/src packages/lc-translator-core/tests"
  },
  "devDependencies": {}
}
```

**Step 4: Verify**

Run:
```bash
uv sync --extra dev
pnpm install
```

Expected: `uv` creates a virtual environment and installs workspace members; `pnpm` installs workspace tooling.

**Step 5: Commit**

```bash
git add pyproject.toml pnpm-workspace.yaml package.json
git commit -m "chore: bootstrap uv and pnpm workspaces"
```


### Task 2: Migrate the existing engine to `lc-translator-core`

**Files:**
- Create: `packages/lc-translator-core/pyproject.toml`
- Migrate: all files under `src/lc_translator/` → `packages/lc-translator-core/src/lc_translator_core/`
- Migrate: `tests/` → `packages/lc-translator-core/tests/`
- Migrate: `scripts/fetch_xsd.py` → `packages/lc-translator-core/scripts/fetch_xsd.py`

**Step 1:** Create `packages/lc-translator-core/pyproject.toml`.

```toml
[project]
name = "lc-translator-core"
version = "0.2.0"
description = "Reusable MT700-to-MX Letter of Credit translation engine"
requires-python = ">=3.9"
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
lc-translator = "lc_translator_core.cli:app"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

**Step 2:** Move source files and update imports from `lc_translator` to `lc_translator_core`.

```bash
mkdir -p packages/lc-translator-core/src
mv src/lc_translator packages/lc-translator-core/src/lc_translator_core
mv tests packages/lc-translator-core/tests
mv scripts packages/lc-translator-core/scripts
```

**Step 3:** Update all internal imports and the CLI entry point.

Change `from lc_translator...` to `from lc_translator_core...` throughout the package and tests.

**Step 4:** Update `packages/lc-translator-core/src/lc_translator_core/__init__.py`.

```python
"""Reusable MT700-to-MX Letter of Credit translation engine."""

from lc_translator_core.__version__ import __version__
from lc_translator_core.exceptions import (
    LcTranslatorError,
    Mt700FormatError,
    ParseResult,
    XsdValidationError,
)
from lc_translator_core.generator import generate_lc
from lc_translator_core.models import LetterOfCredit, Money, Party, Port

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

**Step 5: Verify**

Run:
```bash
uv sync --extra dev
uv run --package lc-translator-core pytest packages/lc-translator-core/tests -v
uv run --package lc-translator-core lc-translator generate --seed 42
```

Expected: all core tests pass and the CLI prints MT700 + MX output.

**Step 6: Commit**

```bash
git add packages/lc-translator-core
git commit -m "refactor: migrate engine to lc-translator-core package"
```


### Task 3: Create the FastAPI service package

**Files:**
- Create: `packages/lc-translator-api/pyproject.toml`
- Create: `packages/lc-translator-api/src/lc_translator_api/main.py`
- Create: `packages/lc-translator-api/src/lc_translator_api/config.py`
- Create: `packages/lc-translator-api/src/lc_translator_api/dependencies.py`
- Create: routers and schemas under `packages/lc-translator-api/src/lc_translator_api/`
- Create: API tests under `packages/lc-translator-api/tests/`

**Step 1:** Create `packages/lc-translator-api/pyproject.toml`.

```toml
[project]
name = "lc-translator-api"
version = "0.2.0"
description = "FastAPI REST service for the LC Translator engine"
requires-python = ">=3.9"
readme = "README.md"
license = { text = "MIT" }
dependencies = [
    "lc-translator-core",
    "fastapi>=0.110",
    "uvicorn[standard]>=0.29",
    "pydantic-settings>=2.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "httpx>=0.27",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.uv.sources]
lc-translator-core = { path = "../lc-translator-core" }
```

**Step 2:** Create `config.py`.

```python
"""Application settings."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Environment-driven settings."""

    cors_origins: list[str] = ["http://localhost:5173"]
    static_dir: Path | None = None
    xsd_path: Path | None = None
    api_prefix: str = "/api"

    class Config:
        env_prefix = "LC_TRANSLATOR_"


@lru_cache
def get_settings() -> Settings:
    return Settings()
```

**Step 3:** Create `dependencies.py`.

```python
"""Shared FastAPI dependencies."""

from __future__ import annotations

from fastapi import Request

from lc_translator_api.config import Settings, get_settings


def get_xsd_schema(request: Request):
    """Return the preloaded XSD schema from app state."""
    return request.app.state.xsd_schema


def get_settings_dependency() -> Settings:
    return get_settings()
```

**Step 4:** Create routers and schemas.

Implement `/api/generate`, `/api/mt-to-mx`, `/api/validate-mt`, `/api/validate-mx`, `/api/health` following the FastAPI skill principles:
- Pydantic models for request/response validation
- Functional routers
- `HTTPException` for expected errors
- Guard clauses for invalid input

**Step 5:** Create `main.py`.

```python
"""FastAPI application entry point."""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from lc_translator_api.config import get_settings
from lc_translator_api.dependencies import get_settings_dependency
from lc_translator_api.routers import generate, translate, validate
from lc_translator_core.validation import XsdValidator


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings_dependency()
    app.state.xsd_schema = None
    if settings.xsd_path:
        validator = XsdValidator(xsd_path=settings.xsd_path)
        if validator.is_available():
            app.state.xsd_schema = validator._load_schema()
    yield
    app.state.xsd_schema = None


def create_app() -> FastAPI:
    settings = get_settings_dependency()
    app = FastAPI(title="LC Translator API", lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(generate.router, prefix=settings.api_prefix)
    app.include_router(translate.router, prefix=settings.api_prefix)
    app.include_router(validate.router, prefix=settings.api_prefix)

    if settings.static_dir and settings.static_dir.exists():
        app.mount("/", StaticFiles(directory=settings.static_dir, html=True), name="static")

        @app.get("/{full_path:path}")
        async def catch_all(full_path: str):
            index = settings.static_dir / "index.html"
            return FileResponse(index)

    return app


app = create_app()
```

**Step 6: Verify**

Run:
```bash
uv sync --extra dev
uv run --package lc-translator-api pytest packages/lc-translator-api/tests -v
uv run --package lc-translator-api uvicorn lc_translator_api.main:app --reload
```

In another shell, test the health endpoint:
```bash
curl http://localhost:8000/api/health
```

Expected: `{"status":"ok"}`.

**Step 7: Commit**

```bash
git add packages/lc-translator-api
git commit -m "feat: add FastAPI service package with generate, translate, and validate endpoints"
```


### Task 4: Create the React web app

**Files:**
- Create: `apps/web/package.json`
- Create: Vite, Tailwind, and PostCSS configs
- Create: React source files under `apps/web/src/`
- Create: Vitest test files

**Step 1:** Create `apps/web/package.json`.

```json
{
  "name": "web",
  "private": true,
  "version": "0.2.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "test": "vitest run",
    "lint": "eslint . --ext js,jsx --report-unused-disable-directives --max-warnings 0"
  },
  "dependencies": {
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "react-router-dom": "^7.0.0"
  },
  "devDependencies": {
    "@testing-library/react": "^16.0.0",
    "@testing-library/jest-dom": "^6.6.0",
    "@vitejs/plugin-react": "^4.4.0",
    "autoprefixer": "^10.4.0",
    "jsdom": "^24.1.0",
    "postcss": "^8.4.0",
    "tailwindcss": "^3.4.0",
    "vite": "^5.3.0",
    "vitest": "^2.0.0"
  }
}
```

**Step 2:** Create `vite.config.js`.

```javascript
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
  test: {
    environment: "jsdom",
    setupFiles: "./src/tests/setup.js",
  },
});
```

**Step 3:** Create `tailwind.config.js`.

```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {},
  },
  plugins: [],
};
```

**Step 4:** Create `postcss.config.js`.

```javascript
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
};
```

**Step 5:** Create the React app source.

- `index.html` with `<div id="root"></div>` and script tag
- `src/main.jsx` renders `<App />` with `BrowserRouter`
- `src/App.jsx` defines routes and layout
- `src/index.css` includes Tailwind directives
- `src/api/client.js` wraps `fetch` for API calls
- `src/pages/GeneratePage.jsx`, `TranslatePage.jsx`, `ValidatePage.jsx`
- `src/components/Header.jsx`, `MessageBlock.jsx`, `HistoryPanel.jsx`, `ValidationResult.jsx`

**Step 6:** Add localStorage history for recent results.

The API is stateless; persistence lives in the browser. Create `src/lib/history.js` to store up to 10 recent results:

```javascript
const HISTORY_KEY = "lc-translator-history";
const MAX_HISTORY = 10;

export function saveToHistory(type, payload) {
  const existing = JSON.parse(localStorage.getItem(HISTORY_KEY) || "[]");
  const entry = { type, createdAt: Date.now(), payload };
  const next = [entry, ...existing].slice(0, MAX_HISTORY);
  localStorage.setItem(HISTORY_KEY, JSON.stringify(next));
}

export function getHistory() {
  return JSON.parse(localStorage.getItem(HISTORY_KEY) || "[]");
}

export function clearHistory() {
  localStorage.removeItem(HISTORY_KEY);
}
```

Wire `saveToHistory` into the Generate, Translate, and Validate pages after a successful API response. Render `HistoryPanel` on each page to show recent entries and allow loading a previous result back into the view.

Create `src/tests/history.test.js` to verify read/write/clear behavior using a `localStorage` mock.

**Step 7:** Create basic Vitest setup.

```javascript
// apps/web/src/tests/setup.js
import "@testing-library/jest-dom";
```

```jsx
// apps/web/src/tests/GeneratePage.test.jsx
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import GeneratePage from "../pages/GeneratePage";

describe("GeneratePage", () => {
  it("renders the generate button", () => {
    render(<GeneratePage />);
    expect(screen.getByText(/generate/i)).toBeInTheDocument();
  });
});
```

**Step 8: Verify**

Run:
```bash
pnpm install
pnpm --filter web build
pnpm --filter web test
```

Expected: build succeeds, tests pass.

**Step 9: Commit**

```bash
git add apps/web
git commit -m "feat: add React web UI with Vite, Tailwind, localStorage history, and Vitest"
```


### Task 5: Wire frontend to backend in development

**Files:**
- Modify: `apps/web/vite.config.js` (already includes proxy)
- Modify: `packages/lc-translator-api/src/lc_translator_api/main.py` (CORS already configured)
- Create: top-level convenience scripts

**Step 1:** Add root-level `scripts/run-dev.sh` for a one-command dev startup.

```bash
#!/usr/bin/env bash
set -euo pipefail

# Start the API in the background
uv run --package lc-translator-api uvicorn lc_translator_api.main:app --reload &
API_PID=$!

# Start the web dev server
pnpm --filter web dev

# Clean up the API on exit
trap "kill $API_PID" EXIT
```

**Step 2:** Make the script executable.

```bash
chmod +x scripts/run-dev.sh
```

**Step 3: Verify**

Run:
```bash
./scripts/run-dev.sh
```

Open http://localhost:5173, navigate to Generate, and click the button. Expected: API request succeeds and MT700/MX output is displayed.

**Step 4: Commit**

```bash
git add scripts/run-dev.sh
git commit -m "chore: add unified dev startup script"
```


### Task 6: Add optional Docker Compose

**Files:**
- Create: `docker-compose.yml`
- Create: `packages/lc-translator-api/Dockerfile`

**Step 1:** Create a minimal API Dockerfile that builds the web app and serves it.

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install Node.js for building the React app
RUN apt-get update && apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    npm install -g pnpm && \
    apt-get clean

# Copy source and install dependencies
COPY . .
RUN pip install uv && \
    uv sync --extra dev && \
    pnpm install && \
    pnpm --filter web build

ENV LC_TRANSLATOR_STATIC_DIR=/app/apps/web/dist
EXPOSE 8000

CMD ["uv", "run", "--package", "lc-translator-api", "uvicorn", "lc_translator_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Step 2:** Create `docker-compose.yml`.

```yaml
services:
  api:
    build:
      context: .
      dockerfile: packages/lc-translator-api/Dockerfile
    ports:
      - "8000:8000"
    environment:
      LC_TRANSLATOR_STATIC_DIR: /app/apps/web/dist
```

**Step 3: Verify**

Run:
```bash
docker compose up --build
```

Expected: app builds, container starts, and http://localhost:8000 serves the React UI with working API.

**Step 4: Commit**

```bash
git add docker-compose.yml packages/lc-translator-api/Dockerfile
git commit -m "chore: add optional Docker Compose setup"
```


### Task 7: Update documentation

**Files:**
- Modify: `README.md`

**Step 1:** Rewrite the root README to describe the monorepo layout and commands.

Include:
- Project overview and architecture diagram
- Prerequisites (`uv`, `pnpm`, `Node 20`)
- Quick start commands
- Development workflow
- Docker Compose option
- Testing commands
- Project structure

**Step 2: Verify**

Run:
```bash
uv run pytest
pnpm --filter web test
uv run ruff check packages
uv run mypy packages
```

Expected: all checks pass.

**Step 3: Commit**

```bash
git add README.md
git commit -m "docs: update README for monorepo architecture"
```


## Verification Summary

After all tasks complete:

- [ ] `uv sync --extra dev` installs both Python packages.
- [ ] `pnpm install` installs the React app.
- [ ] `uv run --package lc-translator-core lc-translator generate --seed 42` still works.
- [ ] `uv run --package lc-translator-api pytest packages/lc-translator-api/tests -v` passes.
- [ ] `uv run --package lc-translator-core pytest packages/lc-translator-core/tests -v` passes.
- [ ] `pnpm --filter web test` passes.
- [ ] `pnpm --filter web build` produces `apps/web/dist/`.
- [ ] `./scripts/run-dev.sh` serves the React UI on `localhost:5173` with API proxy.
- [ ] FastAPI with `LC_TRANSLATOR_STATIC_DIR=apps/web/dist` serves the built UI on `localhost:8000`.
- [ ] `docker compose up --build` runs the full stack.
- [ ] Linting and type checking pass: `uv run ruff check packages`, `uv run mypy packages`.
