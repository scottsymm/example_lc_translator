title: LC Translator Monorepo — Technical Discovery
 tags:
   - discovery
   - lc-translator-monorepo
   - fintech
   - swift
   - iso-20022
   - monorepo
   - react
   - fastapi
 keywords:
   - SWIFT MT700
   - ISO 20022 tsrv.001
   - Letter of Credit
   - trade finance
   - monorepo
   - uv workspaces
   - pnpm workspaces
    - React
    - FastAPI
    - Vite
    - Tailwind CSS
    - Vitest
    - Docker Compose
 discovered: 2026-07-31
 
 # LC Translator Monorepo — Technical Discovery
 
 ## Questions to Resolve
 
 1. Which styling approach should the React app use?
 2. How should the FastAPI backend serve the React frontend in a demo setting?
 3. Should v1 include Docker Compose?
 4. What test stack should the React app use?
 5. What API route prefix and CORS strategy should we use?
 6. How should the API package be structured?
 7. Should we use a task runner for unified monorepo commands?
 8. How should generated and converted results be stored?
 
 ## Findings & Decisions
 
  ### 1. React styling approach
  **Decision:** Tailwind CSS.
  
  **Rationale:**
  - Tailwind provides a consistent, utility-first design system that lets us build a polished UI quickly without writing a lot of custom CSS.
  - It works well with plain JavaScript and Vite; setup is minimal (`tailwindcss`, `postcss`, `autoprefixer`).
  - Responsive design and spacing/sizing defaults are built in, which is useful for a demo that may be viewed on different screen sizes.
  - Component libraries like shadcn/ui require TypeScript, which conflicts with the v1 JavaScript decision. Chakra UI and Mantine are alternatives, but Tailwind keeps the bundle lighter and the JSX more transparent.
  - The trade-off is utility-class-heavy markup; we will mitigate this by extracting small, named components and using `@apply` sparingly for repeated patterns.
 
 ### 2. Serving the React frontend from FastAPI
 **Decision:** FastAPI serves the built React app as static files; API routes live under `/api`.
 
 **Rationale:**
 - During development, the React dev server (`pnpm --filter web dev`) can proxy API requests to FastAPI, or FastAPI can allow CORS for `localhost:5173`.
 - For demos, a single running service is simpler than two separate ports.
 - FastAPI's `StaticFiles(directory="apps/web/dist")` mounted at `/` plus a catch-all route returning `index.html` enables client-side routing with `react-router-dom`.
 - All API routes use `/api` prefix (e.g., `/api/generate`, `/api/health`) to avoid collisions with frontend routes.
 - CORS is only needed in development; production uses same-origin requests.
 
 ### 3. Docker Compose for v1
 **Decision:** Include a minimal `docker-compose.yml` as an optional convenience.
 
 **Rationale:**
 - There is no database or external dependency, so the compose file is simple: one service for the API that also serves the built static frontend.
 - It makes the demo runnable with one command: `docker compose up`.
 - Mark it optional so local development can still use `uv` + `pnpm` directly.
 - Exclude complex multi-stage builds or separate frontend container to avoid scope creep.
 
 ### 4. React test stack
 **Decision:** Vitest + React Testing Library.
 
 **Rationale:**
 - Vite is already the build tool; Vitest is the native test runner and requires minimal configuration.
 - React Testing Library is the standard for component testing.
 - Keep v1 tests focused on component rendering and user interactions (e.g., clicking "Generate" triggers a fetch mock).
 - `jsdom` via Vitest handles DOM simulation.
 
 ### 5. API route prefix and CORS
 **Decision:**
 - All API routes mounted under `/api`.
 - CORS configured via FastAPI middleware, restricted to `http://localhost:5173` in development.
 - In production/demo mode, CORS is unnecessary because the backend serves the frontend from the same origin.
 
 ### 6. API package structure
 **Decision:**
 
 ```
 packages/lc-translator-api/
 ├── pyproject.toml
 ├── src/
 │   └── lc_translator_api/
 │       ├── __init__.py
 │       ├── main.py              # FastAPI app, lifespan, middleware, mount static
 │       ├── config.py            # settings (CORS origins, static dir, XSD path)
 │       ├── dependencies.py      # shared deps (e.g., settings singleton)
 │       ├── routers/
 │       │   ├── __init__.py
 │       │   ├── generate.py
 │       │   ├── translate.py
 │       │   └── validate.py
 │       └── schemas/
 │           ├── __init__.py
 │           ├── generate.py
 │           ├── translate.py
 │           └── validate.py
 └── tests/
     ├── test_health.py
     ├── test_generate.py
     ├── test_translate.py
     └── test_validate.py
 ```
 
 **Rationale:**
 - Functional routers align with the installed `fastapi-python` skill guidance.
 - Schemas live next to routers, grouped by domain concern.
 - `main.py` is the composition root: it wires routers, configures middleware, and optionally mounts static files.
 - `config.py` uses `pydantic-settings` or a small typed config module for environment-driven values.
 
  ### 7. Unified monorepo commands
  **Decision:** Use root `package.json` scripts for frontend and convenience, plus root `pyproject.toml` scripts for Python. Avoid adding Task/Just for v1.
  
  **Rationale:**
  - `package.json` scripts are the expected interface for JavaScript developers.
  - `uv` commands are the expected interface for Python developers.
  - A small `scripts/` directory with shell helpers is acceptable if needed, but root scripts should cover 90% of daily tasks.
  - Example root `package.json` scripts:
    - `dev:web`: start React dev server
    - `dev:api`: start FastAPI dev server
    - `build:web`: build the React app into `apps/web/dist`
    - `test:web`: run Vitest
    - `test:api`: run `uv run pytest` in the API package
  
  ### 8. Result storage
  **Decision:** The API remains stateless. The React UI uses optional browser `localStorage` to remember up to 10 recent results.
  
  **Rationale:**
  - A database or server-side file store is overkill for v1 and would introduce ops complexity.
  - Stateless API endpoints are easier to test, demo, and reason about.
  - Browser `localStorage` gives users a convenient way to revisit recent generated/translated messages without any backend changes.
  - History is per-browser and can be cleared by the user. It is not shared or durable across devices.
  - If cross-session, shared, or durable storage is needed later, it should be designed as a v2 feature with a real persistence layer (SQLite/PostgreSQL + documents table).
 
 ## Implementation Notes
 
 ### FastAPI lifespan for XSD loading
 Load the bundled XSD once at startup using a lifespan context manager. This avoids repeated filesystem reads during validation calls.
 
 ```python
 from contextlib import asynccontextmanager
 from fastapi import FastAPI
 
 @asynccontextmanager
 async def lifespan(app: FastAPI):
     app.state.xsd_schema = load_xsd_schema()
     yield
     app.state.xsd_schema = None
 
 app = FastAPI(lifespan=lifespan)
 ```
 
 ### Static file catch-all for React Router
 After mounting `StaticFiles`, add a catch-all route that returns `apps/web/dist/index.html` for any non-API path. This allows `react-router-dom` to handle `/translate` and `/validate` client-side.
 
 ### API dependency on core package
 In `packages/lc-translator-api/pyproject.toml`:
 
 ```toml
 [project]
 dependencies = [
     "lc-translator-core",
     "fastapi",
     "uvicorn",
     "pydantic-settings",
 ]
 
 [tool.uv.sources]
 lc-translator-core = { path = "../lc-translator-core" }
 ```
 
  ## Open Questions Resolved
  
  - **Storage:** API stateless; React UI uses `localStorage` history for up to 10 recent results.
  
  ## Open Questions Remaining for `write-plan`
  
  - Exact React component breakdown and route structure.
  - Whether to include a simple Makefile or `scripts/run.sh` in addition to package scripts.
  - Whether to keep the original top-level `src/` as a symlink/shim during transition or remove it immediately.
  - Naming conventions for the core package public API (`lc_translator_core` vs a shorter alias).
