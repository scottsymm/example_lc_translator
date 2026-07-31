title: LC Translator Monorepo — Web UI + REST API — Spec
 tags:
   - spec
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
   - Tailwind CSS
   - FastAPI
   - REST API
 distilled: 2026-07-31
 
 # LC Translator Monorepo — Web UI + REST API — Spec
 
 ## Problem Statement
 
 The existing `lc-translator` is a credible CLI demo that translates a Letter of Credit from SWIFT MT700 to ISO 20022 `tsrv.001`. However, a CLI-only tool is hard to demonstrate interactively to senior developers and a CTO. There is no web surface for exploring the translation pipeline, and the engine is tightly coupled to a single CLI entry point rather than reusable by other interfaces.
 
 ## Target Audience
 
 Primary: senior developers and the CTO at Trade Technologies evaluating the project as a full-stack technical demonstration.
 
 Secondary: front-end and back-end engineers who may extend the platform later.
 
 ## Core Value Proposition
 
 A single monorepo that:
 1. Refactors the existing CLI engine into a reusable Python library (`lc-translator-core`).
 2. Exposes the engine through a FastAPI REST service (`lc-translator-api`).
 3. Provides a React web UI (`apps/web`) for interactive LC generation, translation, and validation.
 4. Uses modern workspace tooling (`uv` for Python, `pnpm` for JavaScript) so the project is easy to run and extend.
 5. Keeps the original CLI intact and runnable.
 
 ## Technical Decisions
 
 ### Monorepo tool stack
 - **Python packages:** `uv` workspaces. Root `pyproject.toml` declares `packages/*` as workspace members. The API depends on the core package via `{ path = "../lc-translator-core" }`.
 - **JavaScript app:** `pnpm` workspaces. Root `pnpm-workspace.yaml` declares `apps/*`.
 - **Why not npm?** `pnpm` is the current community default for JavaScript monorepos: faster installs, stricter dependency resolution, and better disk efficiency.
 - **Why not a unified workspace manager?** Tools like Nx or Turborepo are useful for large teams but add unnecessary complexity for one Python API + one React app.
 
 ### Backend architecture
 - **Framework:** FastAPI with Pydantic v2 for request/response validation.
 - **Router style:** Functional routers grouped by concern (`generate.py`, `translate.py`, `validate.py`).
 - **Lifecycle:** Use FastAPI `lifespan` context managers for startup/shutdown if needed (e.g., loading the bundled XSD once).
 - **Error handling:** Use `HTTPException` for expected errors; return structured error responses. Guard clauses for input validation at route entry points.
 - **CORS:** Configured broadly for local development (`localhost:5173` for Vite) and disabled/restricted in production.
 - **Server:** `uvicorn` as the ASGI server.
 
 ### Frontend architecture
 - **Framework:** React 19 with JavaScript (ES2023+).
 - **Build tool:** Vite for fast dev server and production builds.
 - **Styling:** Tailwind CSS for rapid, consistent, utility-first styling.
 - **State:** Local component state and `fetch` for API calls. No global state library for v1.
 - **Client-side persistence:** Optional `localStorage` history (up to 10 entries) so users can revisit recent generated/translated results.
 - **Routing:** `react-router-dom` for multi-page navigation (Generate, Translate, Validate).
 
 ### Package boundaries
 - `packages/lc-translator-core` — domain models, generator, MT700 serializer/parser, MX generator, validation. No FastAPI or web dependencies.
 - `packages/lc-translator-api` — FastAPI app, routers, Pydantic schemas. Depends only on `lc-translator-core`.
 - `apps/web` — React frontend. Communicates with the API over HTTP; no direct Python dependency.
 
 ## MVP Scope
 
 ### Included
 - Refactor existing `src/lc_translator/` into `packages/lc-translator-core/`.
 - Root `pyproject.toml` with `uv` workspace configuration.
 - `packages/lc-translator-api/` FastAPI app with endpoints:
   - `POST /generate` — generate a fake LC and run the full pipeline
   - `POST /mt-to-mx` — translate MT700 text to MX XML
   - `POST /validate-mt` — validate MT700 structure
   - `POST /validate-mx` — validate MX XML against XSD
   - `GET /health` — health check
 - `apps/web/` React app with routes:
   - `/generate` — trigger `/generate` and display MT700 + MX output
   - `/translate` — paste MT700 text, call `/mt-to-mx`, display XML
   - `/validate` — validate MT700 or MX input
 - Optional `localStorage` history panel on each page to reload recent results.
 - Root `package.json` and `pnpm-workspace.yaml`.
 - Updated root README with monorepo setup and run instructions.
 - Tests for the core package (migrated), API route tests with `TestClient`, and basic React component tests with Vitest.
 
 ### Excluded from v1
 - Authentication or authorization.
 - Database persistence.
 - Production deployment configuration (Docker optional, not required).
 - TypeScript on the frontend (v1 stays plain JavaScript).
 - Real-time updates or WebSockets.
 - Additional SWIFT message types beyond MT700.
 
 ## API Contract (v1)
 
 ### `POST /generate`
 Request: optional seed (`?seed=42`) and optional `strict` flag.
 Response: JSON with `letter_of_credit`, `mt700`, `mx_xml`, and validation results.
 
 ### `POST /mt-to-mx`
 Request body: `{ "mt700": "..." }`.
 Response: `{ "mx_xml": "...", "warnings": [...], "errors": [...] }`.
 
 ### `POST /validate-mt`
 Request body: `{ "mt700": "..." }`.
 Response: `{ "valid": true, "errors": [...] }`.
 
 ### `POST /validate-mx`
 Request body: `{ "mx_xml": "..." }`.
 Response: `{ "valid": true, "errors": [...] }`.
 
 ### `GET /health`
 Response: `{ "status": "ok" }`.
 
 ## Success Metrics
 
 - `uv sync` installs all Python workspace members in one command.
 - `pnpm install` installs the React app dependencies.
 - The API starts with `uv run --package lc-translator-api uvicorn lc_translator_api.main:app`.
 - The React dev server starts with `pnpm --filter web dev`.
 - The `/generate` endpoint returns valid MT700 and MX XML.
 - The React UI can trigger `/generate` and render the response.
 - Existing CLI still runs via the core package.
 
 ## Key Risks & Open Questions
 
 - **Refactor risk:** Moving the existing engine into a workspace package must not break current tests or CLI behavior. Mitigation: keep tests passing throughout the refactor.
 - **JavaScript skill gap:** Most modern React skills assume TypeScript. We may need to rely on the `javascript-pro` skill and general React knowledge for plain JavaScript patterns.
 - **CORS in production:** v1 is local-only, but if the demo is served from a non-localhost domain, CORS will need explicit origin configuration.
 - **XSD loading:** The API should load the bundled `tsrv.001` XSD once at startup (via lifespan) to avoid repeated filesystem reads.
 - **Frontend error display:** API validation errors should be surfaced clearly in the React UI, including MT700 parse warnings and XSD validation failures.
 - **Build integration:** Should `pnpm build` output be served statically by the FastAPI app, or should frontend and backend remain on separate ports? Decide during `write-plan`.
