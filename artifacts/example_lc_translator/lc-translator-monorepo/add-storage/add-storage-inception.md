title: Add Storage to LC Translator
 tags:
   - inception
   - lc-translator-monorepo
   - storage
   - persistence
   - postgres
   - sqlalchemy
   - alembic
 keywords:
   - Letter of Credit
   - SWIFT MT700
   - ISO 20022 tsrv.001
   - persistence
   - PostgreSQL
   - SQLite
   - SQLAlchemy
   - Alembic
   - database
   - FastAPI
 incepted: 2026-07-31

 # Add Storage to LC Translator

 ## Idea

 Extend the LC Translator monorepo from a stateless, in-memory demo into a system that persists generated and translated letters of credit. Users (and the API) should be able to save, list, retrieve, and re-run previously created LC artifacts. Storage is the first step toward multi-user demos, audit trails, and a credible product surface.

 This positions the project as more than a one-off translation utility — it becomes a small but credible application with real data persistence.

 ## Goal

 - **Success criteria**
   - Add a persistent storage layer to the `lc-translator-api` package.
   - Store generated/translated LC records with enough metadata to reproduce the original output.
   - Expose REST endpoints for CRUD operations over stored records.
   - Keep storage implementation swappable between local development (SQLite) and shared/demo environments (PostgreSQL).
   - Provide database migrations so schema changes can be tracked and applied.
   - Update the React web UI to save, list, and reload recent records (replacing or extending the current `localStorage` history).
   - Keep the core engine stateless and unchanged; storage belongs in the API layer.
   - Preserve all existing tests and ensure new storage functionality is tested.
   - Keep setup simple: a developer should be able to run the stack with SQLite out of the box.

 - **v1 feature list**
   - Storage model (`LCRecord`) capturing:
     - A stable ID (UUID or auto-increment integer).
     - Timestamps (`created_at`, `updated_at`).
     - Optional human-readable name/title.
     - Source type (`generated`, `translated`, `validated`).
     - The input MT700 text or generated LC seed/strict flags.
     - The output MX XML.
     - Validation results (MT + MX) as structured JSON.
   - SQLAlchemy ORM models and a repository pattern for data access.
   - Alembic migrations initialized under `packages/lc-translator-api/`.
   - FastAPI endpoints:
     - `POST /records` — save a new record from the current pipeline output.
     - `GET /records` — list records with pagination and optional source-type filter.
     - `GET /records/{id}` — fetch a single record.
     - `PUT /records/{id}` — update name/notes.
     - `DELETE /records/{id}` — delete a record.
     - `POST /records/{id}/rerun` — re-run the stored input through the engine and return fresh output.
   - Database URL configured via environment variable (`DATABASE_URL` / `LC_TRANSLATOR_DATABASE_URL`).
   - Default to SQLite for local development; support PostgreSQL via `asyncpg` or `psycopg`.
   - Lifespan-managed engine/session initialization in FastAPI.
   - Update the React app:
     - Add a "Save" button on Generate/Translate/Validate pages.
     - Add a "History" / "Records" view to list, inspect, and reload saved records.
     - Replace or extend the existing `localStorage` history with server-side storage.
   - Tests:
     - Unit tests for the repository layer using an in-memory SQLite database.
     - API route tests for all new endpoints.
     - Optional React component tests for the new Records view.

 - **Open questions**
   - SQLite (simpler local setup) or PostgreSQL (production-like demo) as the default for development?
   - Should the API use synchronous SQLAlchemy or async SQLAlchemy with `AsyncSession`?
   - How should the React UI handle offline/unavailable API — fall back to `localStorage`, show an error, or both?
   - Should records be immutable once created, or allow editing the name/notes only?
   - Do we need soft deletes or hard deletes for v1?
   - Should the API expose a health check that includes database connectivity?
   - Which skills to install before `execute-plan`?
     - `mindrally/skills@fastapi-python` for API design and dependency patterns.
     - `opencode/skills@python-configuration` for environment-based database configuration.
     - `opencode/skills@python-testing-patterns` for repository and integration testing.

 ## Interview Results

 **What is the actual problem you want to solve here?**
 The demo currently loses every translation result when the page is refreshed. We want to add persistence so users can save, review, and re-run past LC translations.

 **Who is this demonstration for?**
 Senior developers and the CTO at Trade Technologies, plus anyone evaluating the platform as a credible product prototype.

 **Why add storage now?**
 Persistence is a baseline expectation for any real application. Adding it now lets the demo support audit trails, history, and eventually user accounts or multi-session workflows.

 **Which database should be used?**
 Default to SQLite for zero-config local development, but design the layer so PostgreSQL can be swapped in with an environment variable.

 **Should the core engine change?**
 No. Storage belongs in the API layer. The `lc-translator-core` package should remain stateless and reusable.

 **Should the existing `localStorage` history remain?**
 It can be retained as a lightweight fallback or replaced entirely by server-side records. This is flagged as an open question.

 ## Timeline

 - Incepted: 2026-07-31
 - Target tech-incept and tech-discovery: within the next session
 - Target write-plan: after storage technology choices are confirmed
 - v1 implementation target: TBD based on scheduling
