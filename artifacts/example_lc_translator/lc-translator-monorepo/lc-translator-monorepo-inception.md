title: LC Translator Monorepo — Web UI + REST API
 tags:
   - inception
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
 incepted: 2026-07-31
 
 # LC Translator Monorepo — Web UI + REST API
 
 ## Idea
 
 Evolve the existing `lc-translator` command-line demo into a small but credible full-stack platform. The legacy MT700-to-MX translation engine is extracted into a reusable Python library, then exposed through a FastAPI REST service and a React web UI. The entire stack lives in a single monorepo managed with modern tooling: `uv` workspaces for Python packages and `pnpm` workspaces for the React application.
 
 This positions the project as more than a one-off demo — it becomes a minimal product surface that senior developers and the CTO can run locally, inspect, and extend.
 
 ## Goal
 
 - **Success criteria**
   - Refactor the existing `lc-translator` engine into a standalone, reusable Python package (`lc-translator-core`).
   - Provide a FastAPI service (`lc-translator-api`) that exposes endpoints for generating, parsing, translating, and validating LC messages.
   - Provide a React web UI (`apps/web`) that interacts with the API and displays MT700 / MX output side by side.
   - Use `uv` workspaces so the API depends on the core package via an editable path dependency.
   - Use `pnpm` workspaces so the React app is installable alongside the Python code.
   - Keep the original CLI demo runnable (the core package still ships a CLI entry point).
   - Include a root-level README with monorepo setup, architecture, and run instructions.
   - Include tests for the API and core package; include basic component tests for the React UI.
   - Preserve existing behavior: MT700 generation, parsing, MX generation, and XSD validation.
 
 - **v1 feature list**
   - `packages/lc-translator-core/`
     - Extract current `src/lc_translator/` into this package.
     - Keep the `lc-translator` CLI entry point.
     - Clean public API surface for use by the API package.
   - `packages/lc-translator-api/`
     - FastAPI application with endpoints:
       - `POST /generate` — generate a fake LC and run the full pipeline
       - `POST /mt-to-mx` — accept MT700 text and return MX XML
       - `POST /validate-mt` — validate MT700 structure
       - `POST /validate-mx` — validate MX XML against XSD
       - `GET /health` — health check
     - Pydantic request/response schemas.
     - CORS configured for local React development.
   - `apps/web/`
     - React app (JavaScript, not TypeScript) bootstrapped with Vite.
     - Views:
       - Generate page: trigger `/generate` and display MT700 + MX output
       - Translate page: paste MT700 text, call `/mt-to-mx`, display XML
       - Validate page: validate MT700 or MX input
      - Minimal, clean UI using Tailwind CSS.
   - Root monorepo configuration
     - `pyproject.toml` with `[tool.uv.workspace]` declaring `packages/*`.
     - `pnpm-workspace.yaml` declaring `apps/*`.
     - Shared lint/test scripts where practical.
   - Documentation
     - Updated root README explaining the monorepo layout.
     - Per-package READMEs with API and UI run instructions.
 
 - **Open questions**
   - Should the React app be plain JavaScript or should we reconsider TypeScript for long-term maintainability?
    - Which Tailwind CSS plugins or custom theme extensions are needed for the demo?
   - Should the API package bundle a startup script that serves the built React UI, or keep frontend and backend on separate ports during development?
   - Do we need authentication for v1, or is this a fully open local demo?
   - How should the API return XSD validation errors — as structured JSON or raw text?
   - Should we add a Docker Compose file to spin up the API + UI together?
   - Which skills to install before `execute-plan`?
     - `mindrally/skills@fastapi-python` (11.7K installs) for API design and patterns.
     - Possibly `manutej/luxor-claude-marketplace@react-patterns` (333 installs) for React guidance, or rely on general knowledge if a stronger JavaScript-specific skill is not available.
 
 ## Interview Results
 
 **What is the actual problem you want to solve here?**
 We want to expand the existing CLI demo into a full-stack platform with a React web UI and a FastAPI REST API, while keeping the core translation engine reusable.
 
 **Who is this demonstration for?**
 Senior developers and the CTO at Trade Technologies.
 
 **Why a monorepo instead of separate repositories?**
 To keep the core engine, API, and frontend in one place so they can be developed, tested, and demoed together. A monorepo also makes it easier to show how the engine is reused across CLI, API, and UI.
 
 **Which JavaScript package manager should we use?**
 We agreed on `pnpm` workspaces for the React app because it is the current community default for JavaScript monorepos and pairs well with `uv` as a modern, fast toolchain.
 
 **Should the React app use TypeScript?**
 The preference is plain JavaScript for v1, but this is flagged as an open question because most modern React skills and examples assume TypeScript.
 
 **What happens to the existing CLI demo?**
 It remains runnable as part of the core package. The monorepo refactor should not break existing behavior or tests.
 
 ## Timeline
 
 - Incepted: 2026-07-31
 - Target tech-incept and tech-discovery: within the next session
 - Target write-plan: after technology choices are confirmed
 - v1 implementation target: TBD based on scheduling
