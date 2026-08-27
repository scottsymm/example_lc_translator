title: Add Storage to LC Translator — Technical Design
 tags:
   - design
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
   - PostgreSQL
   - SQLAlchemy
   - Alembic
   - FastAPI
   - UUID v7
   - Docker Compose
 distilled: 2026-07-31

 # Add Storage to LC Translator — Technical Design

 ## Architecture Overview

 Storage is added to the existing `lc-translator-api` package without changing the stateless `lc-translator-core` engine. The API gains a small persistence layer composed of SQLAlchemy ORM models, a repository module, Alembic migrations, and new FastAPI routers. The React web UI replaces its `localStorage`-based history with server-side records.

 ```
 ┌─────────────┐      HTTP       ┌────────────────────┐      SQL        ┌─────────────┐
 │  apps/web   │ ◄──────────────► │ lc-translator-api  │ ◄──────────────►│  PostgreSQL │
 │  (React)    │                 │  · routers         │                 │             │
 └─────────────┘                 │  · repository      │                 └─────────────┘
                                 │  · SQLAlchemy      │
                                 │  · Alembic         │
                                 └────────────────────┘
                                           │
                                           │ imports
                                           ▼
                                 ┌────────────────────┐
                                 │ lc-translator-core │
                                 │  (stateless)       │
                                 └────────────────────┘
 ```

 ## Components

 ### 1. Database configuration (`lc_translator_api.config`)

 A Pydantic `Settings` class reads `DATABASE_URL` (or `LC_TRANSLATOR_DATABASE_URL`) from the environment. The default in Docker Compose points at the provided PostgreSQL container; for CI/tests a test-specific URL can be injected.

 Example:
 ```python
 DATABASE_URL = "postgresql+psycopg://postgres:postgres@localhost:5432/lc_translator"
 ```

 ### 2. SQLAlchemy session and engine (`lc_translator_api.database`)

 - Synchronous engine created with `create_engine(..., future=True)`.
 - `SessionLocal` sessionmaker bound to the engine.
 - FastAPI dependency `get_db()` yields a `SessionLocal` instance per request.
 - Engine initialization and schema creation happen in the FastAPI lifespan context.

 ### 3. ORM model (`lc_translator_api.models.record`)

 ```python
 class LCRecord(Base):
     __tablename__ = "records"

     id: Mapped[str] = mapped_column(String(36), primary_key=True)
     title: Mapped[str]
     source_type: Mapped[str]  # generated | translated | validated
     created_at: Mapped[datetime]
     updated_at: Mapped[datetime]
     mt700_input: Mapped[str | None]
     generated_seed: Mapped[int | None]
     generated_strict: Mapped[bool | None]
     mx_xml: Mapped[str | None]
     validation_result: Mapped[dict | None]
     lc_model: Mapped[dict | None]
 ```

 - `id` is a UUID v7 string generated in Python before insert.
 - `validation_result` and `lc_model` use `JSONB` via `mapped_column(JSONB)` on PostgreSQL (with a fallback to generic `JSON` for SQLite if compatibility is ever needed).
 - `updated_at` is refreshed on every update.

 ### 4. Persistence DTOs (`lc_translator_api.schemas.record`)

 Pydantic schemas separate the DB representation from internal core models:

 - `RecordCreate` — title, source_type, plus input/output/validation fields.
 - `RecordUpdate` — only mutable fields (title, notes if added later).
 - `RecordOut` — full record response, matching the JSON returned by the API.
 - `RecordSummary` — lightweight list item (id, title, source_type, created_at).

 Mapping between ORM and DTO lives in the repository module.

 ### 5. Repository (`lc_translator_api.repositories.record`)

 A thin repository class (`RecordRepository`) with methods:

 - `create(data: RecordCreate) -> LCRecord`
 - `list(offset: int, limit: int, source_type: str | None) -> list[LCRecord]`
 - `get(record_id: str) -> LCRecord | None`
 - `update(record_id: str, data: RecordUpdate) -> LCRecord | None`
 - `delete(record_id: str) -> bool`

 The repository is instantiated with a SQLAlchemy `Session`. It handles the ORM-to-DTO conversions and raises no HTTP-specific exceptions.

 ### 6. FastAPI routers (`lc_translator_api.routers.records`)

 New router mounted at `/records` with endpoints:

 | Method | Path | Description |
 |---|---|---|
 | `POST` | `/records` | Save a new record |
 | `GET` | `/records` | List records with `limit`, `offset`, optional `source_type` |
 | `GET` | `/records/{id}` | Fetch a single record |
 | `PUT` | `/records/{id}` | Update title/notes |
 | `DELETE` | `/records/{id}` | Delete a record |
 | `POST` | `/records/{id}/rerun` | Re-run the stored input through the engine and return fresh output |

 The `rerun` endpoint uses the stored `source_type` and input fields to reconstruct the pipeline input, calls `lc-translator-core`, and returns the new output without persisting it unless the caller explicitly saves again.

 ### 7. Alembic migrations

 Alembic is initialized under `packages/lc-translator-api/`. The initial migration creates the `records` table. A helper script or `uv run` command applies migrations at startup and in CI.

 ### 8. Docker Compose update

 The root `docker-compose.yml` gains a `db` service running PostgreSQL 16. The `api` service waits for the DB to be healthy before starting and receives `DATABASE_URL` pointing at the `db` service.

 ### 9. React UI changes (`apps/web`)

 - Add a "Save" button on Generate, Translate, and Validate pages.
 - Add a `/records` view listing saved records with pagination.
 - Allow loading a record back into the Generate/Translate/Validate views.
 - Remove or demote the existing `localStorage` history; if the API is unavailable, surface an error rather than silently falling back.

 ## Data Flow

 ### Save a generated record

 1. User clicks **Save** on the Generate page.
 2. React POSTs to `/records` with `source_type=generated`, `generated_seed`, `generated_strict`, `mx_xml`, `validation_result`, and `lc_model`.
 3. Router validates the request with Pydantic.
 4. Repository generates a UUID v7, builds an `LCRecord`, commits it, and maps it to `RecordOut`.
 5. API returns `201 Created` with the saved record.

 ### Save a translated record

 1. User pastes MT700 and clicks **Save** after translation.
 2. React POSTs to `/records` with `source_type=translated`, `mt700_input`, `mx_xml`, `validation_result`, and `lc_model`.
 3. Same persistence flow as above.

 ### List and reload records

 1. User opens `/records`.
 2. React calls `GET /records?limit=20&offset=0`.
 3. API returns `RecordSummary` items ordered by `created_at DESC`.
 4. Selecting a record calls `GET /records/{id}` and loads the full payload back into the active view.

 ### Re-run a record

 1. User selects a saved record and clicks **Re-run**.
 2. React calls `POST /records/{id}/rerun`.
 3. API reads the record, determines the input type, calls the core engine, and returns the fresh result. The original record is not modified.

 ## Key Decisions

 | Decision | Choice | Rationale |
 |---|---|---|
 | Database | PostgreSQL | Production-like persistence; supports JSONB and robust migrations. |
 | IDs | UUID v7 | Opaque, URL-safe, and time-sortable. |
 | SQLAlchemy style | Synchronous + `psycopg3` | Simpler debugging and matches existing FastAPI route style. |
 | Migrations | Alembic | Standard SQLAlchemy migration tooling; tracks schema changes. |
 | Local DB setup | Docker Compose `db` service | Zero-config local Postgres for developers. |
 | Schema shape | Single wide `records` table | Matches the current single-artifact mental model; easy to normalize later. |
 | JSON columns | `JSONB` | Queryable and indexable in PostgreSQL if needed later. |
 | Engine coupling | None | `lc-translator-core` remains stateless; storage lives only in the API. |

 ## Error Handling

 - **Validation errors:** Pydantic returns `422 Unprocessable Entity` with detailed field errors.
 - **Record not found:** Repository returns `None`; router raises `404 Not Found`.
 - **Database connection failure:** Lifespan check fails fast on startup; runtime failures raise `500` with a generic message. Health endpoint includes a lightweight DB ping.
 - **Re-run input mismatch:** If a record has no reproducible input, return `400 Bad Request` with a clear message (e.g., "Record has no MT700 input or generation parameters").

 ## Testing Approach

 - **Repository tests:** Use an in-memory SQLite database via `create_engine("sqlite:///:memory:")` and a fresh schema for each test. These tests verify CRUD, pagination, and filtering without a real Postgres dependency.
 - **API route tests:** Use FastAPI `TestClient` with a repository dependency override pointing at an in-memory session. Verify `201`, `200`, `404`, and `422` paths.
 - **Migration tests:** In CI, apply Alembic migrations against a temporary Postgres container and assert the resulting schema matches the ORM metadata.
 - **React component tests:** Add Vitest tests for the Records list view and Save button interaction using mocked fetch responses.

 ## Open Questions Resolved

 - **SQLite vs PostgreSQL default:** PostgreSQL, with Docker Compose for local setup.
 - **Sync vs async SQLAlchemy:** Synchronous.
 - **ID type:** UUID v7.
 - **localStorage fallback:** Removed in favor of explicit server-side storage; errors are surfaced if the API is unavailable.
 - **Record immutability:** Records are immutable except for the `title` (and optional notes). Re-running produces a new result, not an edit.
 - **Soft deletes:** Hard delete for v1.

 ## Next Step

 This design feeds into `write-plan` to produce `add-storage-plan.md` with tasks, estimates, and implementation order.
