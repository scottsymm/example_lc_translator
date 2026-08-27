# Add Storage to LC Translator — Implementation Plan

*Created: 2026-07-31*

**Goal:** Add PostgreSQL-backed persistence to `lc-translator-api` with Alembic migrations, repository + router layers, and React UI integration while keeping the core engine stateless.

**Architecture:** Synchronous SQLAlchemy 2.0 + `psycopg3` in the API package. Repository pattern isolates DB access from FastAPI routers. Alembic manages migrations. Docker Compose provides a local PostgreSQL service. React replaces `localStorage` history with server-side record CRUD.

**Tech Stack:** PostgreSQL 16, SQLAlchemy 2.0, Alembic, `psycopg3`, `uuid7`, Docker Compose.

**Source:** `artifacts/example_lc_translator/lc-translator-monorepo/add-storage/add-storage-design.md`


## File Map

| File | Action | Responsibility |
|---|---|---|
| `packages/lc-translator-api/pyproject.toml` | Modify | Add `sqlalchemy`, `psycopg`, `alembic`, `uuid7` dependencies |
| `packages/lc-translator-api/src/lc_translator_api/config.py` | Modify | Add `database_url` setting |
| `packages/lc-translator-api/src/lc_translator_api/database.py` | Create | SQLAlchemy engine, sessionmaker, `get_db()` dependency |
| `packages/lc-translator-api/src/lc_translator_api/models/__init__.py` | Create | Package init for ORM models |
| `packages/lc-translator-api/src/lc_translator_api/models/record.py` | Create | `LCRecord` ORM model |
| `packages/lc-translator-api/src/lc_translator_api/schemas/record.py` | Create | Pydantic DTOs: `RecordCreate`, `RecordUpdate`, `RecordOut`, `RecordSummary` |
| `packages/lc-translator-api/src/lc_translator_api/repositories/__init__.py` | Create | Package init for repositories |
| `packages/lc-translator-api/src/lc_translator_api/repositories/record.py` | Create | `RecordRepository` CRUD + list + rerun input helpers |
| `packages/lc-translator-api/src/lc_translator_api/routers/records.py` | Create | FastAPI router for `/records` endpoints |
| `packages/lc-translator-api/src/lc_translator_api/routers/__init__.py` | Modify | Export `records_router` |
| `packages/lc-translator-api/src/lc_translator_api/main.py` | Modify | Initialize engine in lifespan, mount records router |
| `packages/lc-translator-api/src/lc_translator_api/dependencies.py` | Modify | Add `get_db` dependency |
| `packages/lc-translator-api/tests/conftest.py` | Create | Shared test fixtures for in-memory SQLite DB and repository |
| `packages/lc-translator-api/tests/test_records_repository.py` | Create | Repository unit tests against SQLite |
| `packages/lc-translator-api/tests/test_records_api.py` | Create | API route tests with dependency override |
| `packages/lc-translator-api/alembic.ini` | Create | Alembic configuration |
| `packages/lc-translator-api/alembic/env.py` | Create | Alembic environment with sync SQLAlchemy URL |
| `packages/lc-translator-api/alembic/script.py.mako` | Create | Alembic migration template |
| `packages/lc-translator-api/alembic/versions/20260731_0001_create_records_table.py` | Create | Initial migration creating `records` table |
| `packages/lc-translator-api/scripts/migrate.py` | Create | Helper to run Alembic upgrade programmatically |
| `docker-compose.yml` | Modify | Add `db` service and update `api` service env/depends_on |
| `packages/lc-translator-api/Dockerfile` | Modify | Run migrations at container startup |
| `apps/web/src/pages/RecordsPage.jsx` | Create | List/view saved records |
| `apps/web/src/components/SaveRecordButton.jsx` | Create | Button + form to save current result |
| `apps/web/src/api/records.js` | Create | API client functions for records endpoints |
| `apps/web/src/App.jsx` | Modify | Add `/records` route |
| `apps/web/src/pages/GeneratePage.jsx` | Modify | Add Save button wired to `/records` |
| `apps/web/src/pages/TranslatePage.jsx` | Modify | Add Save button wired to `/records` |
| `apps/web/src/pages/ValidatePage.jsx` | Modify | Add Save button wired to `/records` |
| `apps/web/src/hooks/useLocalHistory.js` | Delete or deprioritize | Remove `localStorage` history hook |


## Tasks

### Task 1: Add storage dependencies to API package

**Files:**
- Modify: `packages/lc-translator-api/pyproject.toml`

- [ ] **Step 1: Add dependencies**

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
    "sqlalchemy>=2.0",
    "psycopg>=3.1",
    "alembic>=1.13",
    "uuid7>=0.1",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "httpx>=0.27",
]

[project.scripts]
lc-translator-api-migrate = "lc_translator_api.scripts.migrate:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.uv.sources]
lc-translator-core = { workspace = true }

[tool.hatch.build.targets.wheel]
packages = ["src/lc_translator_api"]
```

- [ ] **Step 2: Verify**

Run: `uv sync --package lc-translator-api`
Expected: succeeds and installs the new packages.

- [ ] **Step 3: Commit**

```bash
git add packages/lc-translator-api/pyproject.toml
git commit -m "deps(api): add sqlalchemy, psycopg, alembic, uuid7"
```


### Task 2: Add database_url to settings

**Files:**
- Modify: `packages/lc-translator-api/src/lc_translator_api/config.py`

- [ ] **Step 1: Add `database_url` setting**

```python
"""Application settings."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Environment-driven settings."""

    model_config = SettingsConfigDict(env_prefix="LC_TRANSLATOR_")

    cors_origins: list[str] = ["http://localhost:5173"]
    static_dir: Optional[Path] = None
    xsd_path: Optional[Path] = None
    api_prefix: str = "/api"
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/lc_translator"


@lru_cache
def get_settings() -> Settings:
    """Return the cached application settings."""
    return Settings()
```

- [ ] **Step 2: Verify**

Run: `uv run --package lc-translator-api python -c "from lc_translator_api.config import get_settings; print(get_settings().database_url)"`
Expected: prints the default Postgres URL.

- [ ] **Step 3: Commit**

```bash
git add packages/lc-translator-api/src/lc_translator_api/config.py
git commit -m "feat(api): add database_url setting"
```


### Task 3: Create database module with engine and session dependency

**Files:**
- Create: `packages/lc-translator-api/src/lc_translator_api/database.py`

- [ ] **Step 1: Write database module**

```python
"""Database engine and session management."""

from __future__ import annotations

from collections.abc import Generator
from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from lc_translator_api.config import Settings, get_settings

_engine: Any = None
_SessionLocal: sessionmaker[Session] | None = None


def init_database(settings: Settings | None = None) -> None:
    """Initialize the SQLAlchemy engine and session factory."""
    global _engine, _SessionLocal
    if settings is None:
        settings = get_settings()
    _engine = create_engine(settings.database_url, future=True)
    _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)


def get_engine() -> Any:
    """Return the initialized engine."""
    if _engine is None:
        raise RuntimeError("Database engine has not been initialized")
    return _engine


def get_session() -> Generator[Session, None, None]:
    """Yield a database session."""
    if _SessionLocal is None:
        raise RuntimeError("Database session factory has not been initialized")
    session = _SessionLocal()
    try:
        yield session
    finally:
        session.close()
```

- [ ] **Step 2: Verify**

Run: `uv run --package lc-translator-api python -c "from lc_translator_api.database import init_database, get_engine; init_database(); print(get_engine())"`
Expected: prints an `Engine` object.

- [ ] **Step 3: Commit**

```bash
git add packages/lc-translator-api/src/lc_translator_api/database.py
git commit -m "feat(api): add sqlalchemy engine and session factory"
```


### Task 4: Create ORM model package and LCRecord model

**Files:**
- Create: `packages/lc-translator-api/src/lc_translator_api/models/__init__.py`
- Create: `packages/lc-translator-api/src/lc_translator_api/models/record.py`

- [ ] **Step 1: Create models package init**

```python
"""ORM models for lc-translator-api."""

from __future__ import annotations

from lc_translator_api.models.record import LCRecord

__all__ = ["LCRecord"]
```

- [ ] **Step 2: Write LCRecord model**

```python
"""ORM model for stored LC records."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import JSON, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """SQLAlchemy declarative base."""


class LCRecord(Base):
    """A persisted LC translation or generation artifact."""

    __tablename__ = "records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    source_type: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    mt700_input: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    generated_seed: Mapped[Optional[int]] = mapped_column(nullable=True)
    generated_strict: Mapped[Optional[bool]] = mapped_column(nullable=True)
    mx_xml: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    validation_result: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    lc_model: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
```

- [ ] **Step 3: Verify**

Run: `uv run --package lc-translator-api python -c "from lc_translator_api.models.record import LCRecord; print(LCRecord.__tablename__)"`
Expected: prints `records`.

- [ ] **Step 4: Commit**

```bash
git add packages/lc-translator-api/src/lc_translator_api/models
git commit -m "feat(api): add LCRecord ORM model"
```


### Task 5: Create Pydantic DTO schemas for records

**Files:**
- Create: `packages/lc-translator-api/src/lc_translator_api/schemas/record.py`

- [ ] **Step 1: Write schemas**

```python
"""Pydantic schemas for stored LC records."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class ValidationResult(BaseModel):
    """Structured validation output."""

    mt700_valid: Optional[bool] = None
    mt700_errors: list[str] = []
    mt700_warnings: list[str] = []
    mx_valid: Optional[bool] = None
    mx_errors: list[str] = []


class RecordCreate(BaseModel):
    """Payload for creating a record."""

    title: Optional[str] = Field(None, description="Optional human-readable title")
    source_type: str = Field(..., description="One of generated, translated, validated")
    mt700_input: Optional[str] = Field(None, description="MT700 input text")
    generated_seed: Optional[int] = Field(None, description="Seed used for generation")
    generated_strict: Optional[bool] = Field(None, description="Strict flag used for generation")
    mx_xml: Optional[str] = Field(None, description="Generated MX XML")
    validation_result: Optional[ValidationResult] = None
    lc_model: Optional[dict[str, Any]] = None


class RecordUpdate(BaseModel):
    """Payload for updating a record."""

    title: Optional[str] = None


class RecordOut(BaseModel):
    """Full record response."""

    id: str
    title: str
    source_type: str
    created_at: datetime
    updated_at: datetime
    mt700_input: Optional[str]
    generated_seed: Optional[int]
    generated_strict: Optional[bool]
    mx_xml: Optional[str]
    validation_result: Optional[ValidationResult]
    lc_model: Optional[dict[str, Any]]

    model_config = {"from_attributes": True}


class RecordSummary(BaseModel):
    """Lightweight record list item."""

    id: str
    title: str
    source_type: str
    created_at: datetime

    model_config = {"from_attributes": True}
```

- [ ] **Step 2: Verify**

Run: `uv run --package lc-translator-api python -c "from lc_translator_api.schemas.record import RecordCreate; print(RecordCreate(source_type='generated'))"`
Expected: prints a valid `RecordCreate` instance.

- [ ] **Step 3: Commit**

```bash
git add packages/lc-translator-api/src/lc_translator_api/schemas/record.py
git commit -m "feat(api): add record pydantic schemas"
```


### Task 6: Create RecordRepository

**Files:**
- Create: `packages/lc-translator-api/src/lc_translator_api/repositories/__init__.py`
- Create: `packages/lc-translator-api/src/lc_translator_api/repositories/record.py`

- [ ] **Step 1: Create repository package init**

```python
"""Repository layer for lc-translator-api."""

from __future__ import annotations

from lc_translator_api.repositories.record import RecordRepository

__all__ = ["RecordRepository"]
```

- [ ] **Step 2: Write repository**

```python
"""Repository for LCRecord persistence."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session
from uuid_extensions import uuid7str

from lc_translator_api.models.record import LCRecord
from lc_translator_api.schemas.record import RecordCreate, RecordUpdate


class RecordRepository:
    """CRUD and query operations for LCRecord."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def create(self, data: RecordCreate) -> LCRecord:
        """Persist a new record."""
        now = datetime.now(timezone.utc)
        record = LCRecord(
            id=uuid7str(),
            title=data.title or f"LC Record {now.isoformat()}",
            source_type=data.source_type,
            created_at=now,
            updated_at=now,
            mt700_input=data.mt700_input,
            generated_seed=data.generated_seed,
            generated_strict=data.generated_strict,
            mx_xml=data.mx_xml,
            validation_result=data.validation_result.model_dump() if data.validation_result else None,
            lc_model=data.lc_model,
        )
        self._session.add(record)
        self._session.commit()
        self._session.refresh(record)
        return record

    def get(self, record_id: str) -> Optional[LCRecord]:
        """Fetch a record by ID."""
        return self._session.get(LCRecord, record_id)

    def list(
        self, offset: int = 0, limit: int = 20, source_type: Optional[str] = None
    ) -> list[LCRecord]:
        """List records ordered by creation time descending."""
        query = self._session.query(LCRecord).order_by(LCRecord.created_at.desc())
        if source_type:
            query = query.where(LCRecord.source_type == source_type)
        return query.offset(offset).limit(limit).all()

    def update(self, record_id: str, data: RecordUpdate) -> Optional[LCRecord]:
        """Update a record's mutable fields."""
        record = self.get(record_id)
        if record is None:
            return None
        if data.title is not None:
            record.title = data.title
        record.updated_at = datetime.now(timezone.utc)
        self._session.commit()
        self._session.refresh(record)
        return record

    def delete(self, record_id: str) -> bool:
        """Delete a record. Returns True if deleted."""
        record = self.get(record_id)
        if record is None:
            return False
        self._session.delete(record)
        self._session.commit()
        return True
```

- [ ] **Step 3: Verify**

Run: `uv run --package lc-translator-api python -c "from lc_translator_api.repositories.record import RecordRepository; print(RecordRepository)"`
Expected: prints the class.

- [ ] **Step 4: Commit**

```bash
git add packages/lc-translator-api/src/lc_translator_api/repositories
git commit -m "feat(api): add RecordRepository"
```


### Task 7: Add database dependency and mount records router

**Files:**
- Modify: `packages/lc-translator-api/src/lc_translator_api/dependencies.py`
- Modify: `packages/lc-translator-api/src/lc_translator_api/main.py`
- Modify: `packages/lc-translator-api/src/lc_translator_api/routers/__init__.py`

- [ ] **Step 1: Add get_db dependency**

Edit `packages/lc-translator-api/src/lc_translator_api/dependencies.py`:

```python
"""Shared FastAPI dependencies."""

from __future__ import annotations

from collections.abc import Generator
from typing import Any

from fastapi import Request
from sqlalchemy.orm import Session

from lc_translator_api.config import Settings, get_settings
from lc_translator_api.database import get_session


def get_settings_dependency() -> Settings:
    """Return application settings."""
    return get_settings()


def get_xsd_schema(request: Request) -> Any:
    """Return the preloaded XSD schema from app state."""
    return request.app.state.xsd_schema


def get_db() -> Generator[Session, None, None]:
    """Yield a SQLAlchemy session for the request."""
    yield from get_session()
```

- [ ] **Step 2: Export records_router**

Edit `packages/lc-translator-api/src/lc_translator_api/routers/__init__.py`:

```python
"""API routers."""

from __future__ import annotations

from lc_translator_api.routers.generate import router as generate_router
from lc_translator_api.routers.records import router as records_router
from lc_translator_api.routers.translate import router as translate_router
from lc_translator_api.routers.validate import router as validate_router

__all__ = ["generate_router", "records_router", "translate_router", "validate_router"]
```

- [ ] **Step 3: Initialize DB and mount router in main.py**

Edit `packages/lc-translator-api/src/lc_translator_api/main.py`:

```python
"""FastAPI application entry point."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from lc_translator_core.validation import XsdValidator

from lc_translator_api.database import init_database
from lc_translator_api.dependencies import get_settings_dependency
from lc_translator_api.routers import (
    generate_router,
    records_router,
    translate_router,
    validate_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Load the XSD schema and initialize the database engine once at startup."""
    settings = get_settings_dependency()
    init_database(settings)
    app.state.xsd_schema = None
    validator = XsdValidator(xsd_path=settings.xsd_path) if settings.xsd_path else XsdValidator()
    if validator.is_available():
        app.state.xsd_schema = validator._load_schema()
    yield
    app.state.xsd_schema = None


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings_dependency()
    app = FastAPI(title="LC Translator API", lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(generate_router, prefix=settings.api_prefix)
    app.include_router(translate_router, prefix=settings.api_prefix)
    app.include_router(validate_router, prefix=settings.api_prefix)
    app.include_router(records_router, prefix=settings.api_prefix)

    if settings.static_dir and settings.static_dir.exists():
        app.mount("/", StaticFiles(directory=settings.static_dir, html=True), name="static")

        @app.get("/{full_path:path}")
        async def catch_all(full_path: str) -> FileResponse:
            if settings.static_dir is None:
                raise RuntimeError("static_dir should be set")
            index = settings.static_dir / "index.html"
            return FileResponse(index)

    return app


app = create_app()
```

- [ ] **Step 4: Verify**

Run: `uv run --package lc-translator-api python -c "from lc_translator_api.main import create_app; app = create_app(); print([r.path for r in app.routes])"`
Expected: includes `/api/records` routes.

- [ ] **Step 5: Commit**

```bash
git add packages/lc-translator-api/src/lc_translator_api/dependencies.py \
            packages/lc-translator-api/src/lc_translator_api/routers/__init__.py \
            packages/lc-translator-api/src/lc_translator_api/main.py
git commit -m "feat(api): initialize db and wire records router"
```


### Task 8: Implement records router endpoints

**Files:**
- Create: `packages/lc-translator-api/src/lc_translator_api/routers/records.py`

- [ ] **Step 1: Write records router**

```python
"""Records endpoint router."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from lc_translator_api.dependencies import get_db
from lc_translator_api.repositories.record import RecordRepository
from lc_translator_api.schemas.record import (
    RecordCreate,
    RecordOut,
    RecordSummary,
    RecordUpdate,
)

router = APIRouter(tags=["records"])


def _get_repository(db: Session = Depends(get_db)) -> RecordRepository:
    return RecordRepository(db)


@router.post("/records", response_model=RecordOut, status_code=201)
def create_record(
    payload: RecordCreate, repo: RecordRepository = Depends(_get_repository)
) -> RecordOut:
    """Persist a new LC record."""
    record = repo.create(payload)
    return RecordOut.model_validate(record)


@router.get("/records", response_model=list[RecordSummary])
def list_records(
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    source_type: str | None = Query(None),
    repo: RecordRepository = Depends(_get_repository),
) -> list[RecordSummary]:
    """List saved records."""
    records = repo.list(offset=offset, limit=limit, source_type=source_type)
    return [RecordSummary.model_validate(r) for r in records]


@router.get("/records/{record_id}", response_model=RecordOut)
def get_record(record_id: str, repo: RecordRepository = Depends(_get_repository)) -> RecordOut:
    """Fetch a single record."""
    record = repo.get(record_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Record not found")
    return RecordOut.model_validate(record)


@router.put("/records/{record_id}", response_model=RecordOut)
def update_record(
    record_id: str,
    payload: RecordUpdate,
    repo: RecordRepository = Depends(_get_repository),
) -> RecordOut:
    """Update a record's title."""
    record = repo.update(record_id, payload)
    if record is None:
        raise HTTPException(status_code=404, detail="Record not found")
    return RecordOut.model_validate(record)


@router.delete("/records/{record_id}", status_code=204)
def delete_record(record_id: str, repo: RecordRepository = Depends(_get_repository)) -> None:
    """Delete a record."""
    deleted = repo.delete(record_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Record not found")
```

- [ ] **Step 2: Verify**

Run: `uv run --package lc-translator-api python -c "from lc_translator_api.main import create_app; from fastapi.testclient import TestClient; app = create_app(); print([r.path for r in app.routes if 'records' in str(r.path)])"`
Expected: lists `/api/records`, `/api/records/{record_id}`.

- [ ] **Step 3: Commit**

```bash
git add packages/lc-translator-api/src/lc_translator_api/routers/records.py
git commit -m "feat(api): add records CRUD router"
```


### Task 9: Add repository unit tests

**Files:**
- Create: `packages/lc-translator-api/tests/conftest.py`
- Create: `packages/lc-translator-api/tests/test_records_repository.py`

- [ ] **Step 1: Write test fixtures**

```python
"""Shared pytest fixtures."""

from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from lc_translator_api.models.record import Base, LCRecord
from lc_translator_api.repositories.record import RecordRepository
from lc_translator_api.schemas.record import RecordCreate, ValidationResult


@pytest.fixture
def db_session() -> Session:
    """Create an in-memory SQLite DB and yield a session."""
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def repository(db_session: Session) -> RecordRepository:
    """Return a RecordRepository backed by the test session."""
    return RecordRepository(db_session)


@pytest.fixture
def sample_create() -> RecordCreate:
    """Return a minimal generated record create payload."""
    return RecordCreate(
        source_type="generated",
        generated_seed=42,
        generated_strict=False,
        mx_xml="<Document/>",
        validation_result=ValidationResult(
            mt700_valid=True,
            mt700_errors=[],
            mt700_warnings=[],
            mx_valid=True,
            mx_errors=[],
        ),
    )
```

- [ ] **Step 2: Write repository tests**

```python
"""Tests for RecordRepository."""

from __future__ import annotations

from lc_translator_api.repositories.record import RecordRepository
from lc_translator_api.schemas.record import RecordCreate, RecordUpdate


def test_create_record(repository: RecordRepository, sample_create: RecordCreate) -> None:
    record = repository.create(sample_create)
    assert record.id
    assert record.source_type == "generated"
    assert record.title.startswith("LC Record")


def test_get_record(repository: RecordRepository, sample_create: RecordCreate) -> None:
    created = repository.create(sample_create)
    fetched = repository.get(created.id)
    assert fetched is not None
    assert fetched.id == created.id


def test_get_missing_record(repository: RecordRepository) -> None:
    assert repository.get("not-a-real-id") is None


def test_list_records(repository: RecordRepository, sample_create: RecordCreate) -> None:
    repository.create(sample_create)
    repository.create(sample_create)
    records = repository.list(limit=10)
    assert len(records) == 2


def test_list_filter_by_source_type(
    repository: RecordRepository, sample_create: RecordCreate
) -> None:
    repository.create(sample_create)
    repository.create(RecordCreate(source_type="translated", mt700_input="MT700"))
    generated = repository.list(source_type="generated")
    translated = repository.list(source_type="translated")
    assert len(generated) == 1
    assert len(translated) == 1


def test_update_record(repository: RecordRepository, sample_create: RecordCreate) -> None:
    created = repository.create(sample_create)
    updated = repository.update(created.id, RecordUpdate(title="New Title"))
    assert updated is not None
    assert updated.title == "New Title"


def test_update_missing_record(repository: RecordRepository) -> None:
    assert repository.update("missing-id", RecordUpdate(title="X")) is None


def test_delete_record(repository: RecordRepository, sample_create: RecordCreate) -> None:
    created = repository.create(sample_create)
    assert repository.delete(created.id) is True
    assert repository.get(created.id) is None


def test_delete_missing_record(repository: RecordRepository) -> None:
    assert repository.delete("missing-id") is False
```

- [ ] **Step 3: Verify**

Run: `uv run --package lc-translator-api pytest packages/lc-translator-api/tests/test_records_repository.py`
Expected: all 8 tests pass.

- [ ] **Step 4: Commit**

```bash
git add packages/lc-translator-api/tests/conftest.py \
            packages/lc-translator-api/tests/test_records_repository.py
git commit -m "test(api): add RecordRepository tests"
```


### Task 10: Add API route tests

**Files:**
- Create: `packages/lc-translator-api/tests/test_records_api.py`

- [ ] **Step 1: Write API tests**

```python
"""Tests for records API endpoints."""

from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from lc_translator_api.database import init_database
from lc_translator_api.dependencies import get_db
from lc_translator_api.main import create_app
from lc_translator_api.models.record import Base
from lc_translator_api.schemas.record import RecordCreate, ValidationResult

_engine = create_engine("sqlite:///:memory:", future=True)
Base.metadata.create_all(bind=_engine)
_TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)


def _override_get_db() -> Session:
    session = _TestSessionLocal()
    try:
        yield session
    finally:
        session.close()


app = create_app()
app.dependency_overrides[get_db] = _override_get_db
client = TestClient(app)


def _sample_payload() -> dict:
    return {
        "source_type": "generated",
        "generated_seed": 42,
        "generated_strict": False,
        "mx_xml": "<Document/>",
        "validation_result": {
            "mt700_valid": True,
            "mt700_errors": [],
            "mt700_warnings": [],
            "mx_valid": True,
            "mx_errors": [],
        },
    }


def test_create_record() -> None:
    response = client.post("/api/records", json=_sample_payload())
    assert response.status_code == 201
    data = response.json()
    assert data["id"]
    assert data["source_type"] == "generated"


def test_list_records() -> None:
    client.post("/api/records", json=_sample_payload())
    response = client.get("/api/records")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1


def test_get_record() -> None:
    created = client.post("/api/records", json=_sample_payload()).json()
    response = client.get(f"/api/records/{created['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


def test_get_record_not_found() -> None:
    response = client.get("/api/records/not-real")
    assert response.status_code == 404


def test_update_record() -> None:
    created = client.post("/api/records", json=_sample_payload()).json()
    response = client.put(f"/api/records/{created['id']}", json={"title": "Updated"})
    assert response.status_code == 200
    assert response.json()["title"] == "Updated"


def test_delete_record() -> None:
    created = client.post("/api/records", json=_sample_payload()).json()
    response = client.delete(f"/api/records/{created['id']}")
    assert response.status_code == 204
    assert client.get(f"/api/records/{created['id']}").status_code == 404
```

- [ ] **Step 2: Verify**

Run: `uv run --package lc-translator-api pytest packages/lc-translator-api/tests/test_records_api.py`
Expected: all 6 tests pass.

- [ ] **Step 3: Commit**

```bash
git add packages/lc-translator-api/tests/test_records_api.py
git commit -m "test(api): add records API route tests"
```


### Task 11: Initialize Alembic and write initial migration

**Files:**
- Create: `packages/lc-translator-api/alembic.ini`
- Create: `packages/lc-translator-api/alembic/env.py`
- Create: `packages/lc-translator-api/alembic/script.py.mako`
- Create: `packages/lc-translator-api/alembic/versions/20260731_0001_create_records_table.py`

- [ ] **Step 1: Create alembic.ini**

```ini
[alembic]
script_location = alembic
prepend_sys_path = .
version_path_separator = os
sqlalchemy.url = postgresql+psycopg://postgres:postgres@localhost:5432/lc_translator

[post_write_hooks]

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
```

- [ ] **Step 2: Create alembic/env.py**

```python
"""Alembic environment configuration."""

from __future__ import annotations

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from lc_translator_api.config import get_settings
from lc_translator_api.models.record import Base

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_url() -> str:
    return get_settings().database_url


def run_migrations_offline() -> None:
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = get_url()
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

- [ ] **Step 3: Create alembic/script.py.mako**

```mako
"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# revision identifiers, used by Alembic.
revision: str = ${repr(up_revision)}
down_revision: Union[str, None] = ${repr(down_revision)}
branch_labels: Union[str, Sequence[str], None] = ${repr(branch_labels)}
depends_on: Union[str, Sequence[str], None] = ${repr(depends_on)}


def upgrade() -> None:
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    ${downgrades if downgrades else "pass"}
```

- [ ] **Step 4: Write initial migration**

```python
"""create records table

Revision ID: 20260731_0001
Revises:
Create Date: 2026-07-31 00:00:00.000000

"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "20260731_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "records",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("source_type", sa.String(32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("mt700_input", sa.Text(), nullable=True),
        sa.Column("generated_seed", sa.Integer(), nullable=True),
        sa.Column("generated_strict", sa.Boolean(), nullable=True),
        sa.Column("mx_xml", sa.Text(), nullable=True),
        sa.Column("validation_result", sa.JSON(), nullable=True),
        sa.Column("lc_model", sa.JSON(), nullable=True),
    )
    op.create_index("ix_records_created_at", "records", ["created_at"])
    op.create_index("ix_records_source_type", "records", ["source_type"])


def downgrade() -> None:
    op.drop_index("ix_records_source_type", table_name="records")
    op.drop_index("ix_records_created_at", table_name="records")
    op.drop_table("records")
```

- [ ] **Step 5: Create migration helper script**

Create `packages/lc-translator-api/src/lc_translator_api/scripts/__init__.py` (empty) and `packages/lc-translator-api/src/lc_translator_api/scripts/migrate.py`:

```python
"""CLI helper to run Alembic migrations."""

from __future__ import annotations

from alembic import command
from alembic.config import Config

from lc_translator_api.config import get_settings


def main() -> None:
    settings = get_settings()
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", settings.database_url)
    command.upgrade(alembic_cfg, "head")


if __name__ == "__main__":
    main()
```

- [ ] **Step 6: Verify**

Run: `uv run --package lc-translator-api python -m alembic check`
Expected: succeeds with no output (or a message indicating no new revisions).

- [ ] **Step 7: Commit**

```bash
git add packages/lc-translator-api/alembic.ini \
            packages/lc-translator-api/alembic \
            packages/lc-translator-api/src/lc_translator_api/scripts
git commit -m "chore(api): add alembic migrations and records table"
```


### Task 12: Update Docker Compose with PostgreSQL service

**Files:**
- Modify: `docker-compose.yml`
- Modify: `packages/lc-translator-api/Dockerfile`

- [ ] **Step 1: Update docker-compose.yml**

```yaml
services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: lc_translator
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

  api:
    build:
      context: .
      dockerfile: packages/lc-translator-api/Dockerfile
    ports:
      - "8000:8000"
    environment:
      LC_TRANSLATOR_STATIC_DIR: /app/apps/web/dist
      LC_TRANSLATOR_DATABASE_URL: postgresql+psycopg://postgres:postgres@db:5432/lc_translator
    depends_on:
      db:
        condition: service_healthy

volumes:
  postgres_data:
```

- [ ] **Step 2: Update Dockerfile to run migrations**

Read `packages/lc-translator-api/Dockerfile` first, then modify the entrypoint/CMD to run migrations before starting uvicorn. Example change:

```dockerfile
CMD ["sh", "-c", "uv run --package lc-translator-api lc-translator-api-migrate && uv run --package lc-translator-api uvicorn lc_translator_api.main:app --host 0.0.0.0 --port 8000"]
```

(If the Dockerfile uses a different structure, preserve it and add the migration command at the appropriate stage.)

- [ ] **Step 3: Verify**

Run: `docker compose config`
Expected: validates successfully and includes `db` and `api` services.

- [ ] **Step 4: Commit**

```bash
git add docker-compose.yml packages/lc-translator-api/Dockerfile
git commit -m "chore(docker): add postgres service and migration startup"
```


### Task 13: Add React records API client

**Files:**
- Create: `apps/web/src/api/records.js`

- [ ] **Step 1: Write records API client**

```javascript
const API_BASE = import.meta.env.VITE_API_BASE_URL || "/api";

async function fetchJson(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(error.detail || `Request failed: ${response.status}`);
  }
  if (response.status === 204) {
    return null;
  }
  return response.json();
}

export function listRecords(params = {}) {
  const search = new URLSearchParams();
  if (params.offset) search.set("offset", String(params.offset));
  if (params.limit) search.set("limit", String(params.limit));
  if (params.source_type) search.set("source_type", params.source_type);
  return fetchJson(`/records?${search.toString()}`);
}

export function getRecord(id) {
  return fetchJson(`/records/${id}`);
}

export function createRecord(record) {
  return fetchJson("/records", {
    method: "POST",
    body: JSON.stringify(record),
  });
}

export function updateRecord(id, updates) {
  return fetchJson(`/records/${id}`, {
    method: "PUT",
    body: JSON.stringify(updates),
  });
}

export function deleteRecord(id) {
  return fetchJson(`/records/${id}`, {
    method: "DELETE",
  });
}
```

- [ ] **Step 2: Verify**

Run: `pnpm --filter web lint` (or `pnpm --filter web test` if a lint script exists).
Expected: no lint errors in the new file.

- [ ] **Step 3: Commit**

```bash
git add apps/web/src/api/records.js
git commit -m "feat(web): add records API client"
```


### Task 14: Add SaveRecordButton component

**Files:**
- Create: `apps/web/src/components/SaveRecordButton.jsx`

- [ ] **Step 1: Write component**

```jsx
import { useState } from "react";
import { createRecord } from "../api/records";

export function SaveRecordButton({ record, onSaved, label = "Save" }) {
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);

  async function handleSave() {
    setSaving(true);
    setError(null);
    try {
      const saved = await createRecord(record);
      onSaved?.(saved);
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="flex flex-col items-start gap-1">
      <button
        type="button"
        onClick={handleSave}
        disabled={saving}
        className="rounded bg-indigo-600 px-4 py-2 text-white hover:bg-indigo-700 disabled:opacity-50"
      >
        {saving ? "Saving..." : label}
      </button>
      {error && <p className="text-sm text-red-600">{error}</p>}
    </div>
  );
}
```

- [ ] **Step 2: Verify**

Run: `pnpm --filter web test -- --run SaveRecordButton` (or equivalent).
Expected: component test file can be added later; for now, lint passes.

- [ ] **Step 3: Commit**

```bash
git add apps/web/src/components/SaveRecordButton.jsx
git commit -m "feat(web): add SaveRecordButton component"
```


### Task 15: Add RecordsPage

**Files:**
- Create: `apps/web/src/pages/RecordsPage.jsx`

- [ ] **Step 1: Write RecordsPage**

```jsx
import { useEffect, useState } from "react";
import { listRecords, deleteRecord } from "../api/records";

export function RecordsPage() {
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const data = await listRecords({ limit: 50 });
      setRecords(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function handleDelete(id) {
    if (!confirm("Delete this record?")) return;
    await deleteRecord(id);
    setRecords((prev) => prev.filter((r) => r.id !== id));
  }

  if (loading) return <p className="p-4">Loading...</p>;
  if (error) return <p className="p-4 text-red-600">{error}</p>;

  return (
    <div className="space-y-4 p-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Saved Records</h1>
        <button
          type="button"
          onClick={load}
          className="rounded bg-gray-200 px-3 py-1 text-sm hover:bg-gray-300"
        >
          Refresh
        </button>
      </div>
      {records.length === 0 ? (
        <p className="text-gray-600">No saved records yet.</p>
      ) : (
        <ul className="divide-y rounded border">
          {records.map((record) => (
            <li key={record.id} className="flex items-center justify-between p-4">
              <div>
                <p className="font-medium">{record.title}</p>
                <p className="text-sm text-gray-600">
                  {record.source_type} · {new Date(record.created_at).toLocaleString()}
                </p>
              </div>
              <button
                type="button"
                onClick={() => handleDelete(record.id)}
                className="text-sm text-red-600 hover:underline"
              >
                Delete
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
```

- [ ] **Step 2: Verify**

Run: `pnpm --filter web lint`
Expected: no errors.

- [ ] **Step 3: Commit**

```bash
git add apps/web/src/pages/RecordsPage.jsx
git commit -m "feat(web): add RecordsPage"
```


### Task 16: Wire records route and add Save buttons

**Files:**
- Modify: `apps/web/src/App.jsx`
- Modify: `apps/web/src/pages/GeneratePage.jsx`
- Modify: `apps/web/src/pages/TranslatePage.jsx`
- Modify: `apps/web/src/pages/ValidatePage.jsx`

- [ ] **Step 1: Add /records route in App.jsx**

Add `RecordsPage` import and route. Preserve existing routes.

```jsx
import { RecordsPage } from "./pages/RecordsPage";

// Inside router/routes:
<Route path="/records" element={<RecordsPage />} />
```

- [ ] **Step 2: Add Save button to GeneratePage.jsx**

Import `SaveRecordButton` and include it in the response section after generating. Build a record payload from the response:

```jsx
const recordPayload = {
  source_type: "generated",
  generated_seed: seed,
  generated_strict: strict,
  mx_xml: result.mx_xml,
  validation_result: {
    mt700_valid: result.mt700_valid,
    mt700_errors: result.mt700_errors,
    mt700_warnings: result.mt700_warnings,
    mx_valid: result.mx_valid,
    mx_errors: result.mx_errors,
  },
};
```

Render `<SaveRecordButton record={recordPayload} />`.

- [ ] **Step 3: Add Save button to TranslatePage.jsx**

Build payload:

```jsx
const recordPayload = {
  source_type: "translated",
  mt700_input: mt700,
  mx_xml: result.mx_xml,
  validation_result: {
    mt700_valid: true, // MT structure was accepted for translation
    mt700_errors: result.errors,
    mt700_warnings: result.warnings,
    mx_valid: result.mx_valid,
    mx_errors: result.mx_errors,
  },
};
```

- [ ] **Step 4: Add Save button to ValidatePage.jsx**

Build payload for `source_type: "validated"` from the validation results. `mx_xml` may be omitted.

- [ ] **Step 5: Add navigation link**

Add a "Records" link in the existing navigation (likely in `App.jsx` or a layout component).

- [ ] **Step 6: Verify**

Run: `pnpm --filter web build`
Expected: build succeeds with no errors.

- [ ] **Step 7: Commit**

```bash
git add apps/web/src/App.jsx \
            apps/web/src/pages/GeneratePage.jsx \
            apps/web/src/pages/TranslatePage.jsx \
            apps/web/src/pages/ValidatePage.jsx
git commit -m "feat(web): wire records route and save buttons"
```


### Task 17: Remove or deprioritize localStorage history

**Files:**
- Modify: `apps/web/src/hooks/useLocalHistory.js` (delete or mark deprecated)

- [ ] **Step 1: Remove usage**

Find all imports of `useLocalHistory` and remove them, replacing any saved-history UI with a link to `/records`.

- [ ] **Step 2: Delete hook file**

```bash
rm apps/web/src/hooks/useLocalHistory.js
```

- [ ] **Step 3: Verify**

Run: `pnpm --filter web build`
Expected: build succeeds.

- [ ] **Step 4: Commit**

```bash
git add apps/web
git commit -m "refactor(web): replace localStorage history with server records"
```


### Task 18: Add rerun endpoint

**Files:**
- Modify: `packages/lc-translator-api/src/lc_translator_api/routers/records.py`

- [ ] **Step 1: Add rerun endpoint**

```python
from lc_translator_api.schemas.generate import GenerateResponse
from lc_translator_api.schemas.translate import TranslateResponse


@router.post("/records/{record_id}/rerun")
def rerun_record(record_id: str, repo: RecordRepository = Depends(_get_repository)) -> Any:
    """Re-run the stored input through the engine and return fresh output."""
    record = repo.get(record_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Record not found")

    if record.source_type == "generated":
        from lc_translator_api.routers.generate import generate_endpoint
        from lc_translator_api.schemas.generate import GenerateRequest

        if record.generated_seed is None or record.generated_strict is None:
            raise HTTPException(status_code=400, detail="Record missing generation parameters")
        return generate_endpoint(
            GenerateRequest(seed=record.generated_seed, strict=record.generated_strict)
        )

    if record.source_type in {"translated", "validated"}:
        from lc_translator_api.routers.translate import translate_endpoint
        from lc_translator_api.schemas.translate import TranslateRequest

        if record.mt700_input is None:
            raise HTTPException(status_code=400, detail="Record missing MT700 input")
        return translate_endpoint(TranslateRequest(mt700=record.mt700_input))

    raise HTTPException(status_code=400, detail=f"Unsupported source_type: {record.source_type}")
```

- [ ] **Step 2: Verify**

Run: `uv run --package lc-translator-api pytest packages/lc-translator-api/tests/test_records_api.py`
Expected: existing tests still pass.

- [ ] **Step 3: Commit**

```bash
git add packages/lc-translator-api/src/lc_translator_api/routers/records.py
git commit -m "feat(api): add record rerun endpoint"
```


### Task 19: Add health check DB ping

**Files:**
- Modify: `packages/lc-translator-api/src/lc_translator_api/routers/health.py` (or create if missing)
- Modify: `packages/lc-translator-api/src/lc_translator_api/main.py`

If no health router exists, create `packages/lc-translator-api/src/lc_translator_api/routers/health.py`:

```python
"""Health check router."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from lc_translator_api.dependencies import get_db

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check(db: Session = Depends(get_db)) -> dict:
    try:
        db.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False
    return {"status": "ok", "database": db_ok}
```

Mount it in `main.py` if not already present.

- [ ] **Step 2: Verify**

Run: `uv run --package lc-translator-api pytest packages/lc-translator-api/tests/test_health.py`
Expected: tests pass (or create a new test if none exists).

- [ ] **Step 3: Commit**

```bash
git add packages/lc-translator-api/src/lc_translator_api/routers/health.py packages/lc-translator-api/src/lc_translator_api/main.py
git commit -m "feat(api): add database health check ping"
```


### Task 20: Update README with storage setup instructions

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Add storage section**

Append to README:

```markdown
## Storage

LC Translator persists translation records in PostgreSQL.

### Run with Docker Compose (recommended)

```bash
docker compose up --build
```

This starts PostgreSQL and runs Alembic migrations automatically.

### Run locally with your own Postgres

```bash
export LC_TRANSLATOR_DATABASE_URL=postgresql+psycopg://user:pass@localhost:5432/lc_translator
uv run --package lc-translator-api alembic upgrade head
uv run --package lc-translator-api uvicorn lc_translator_api.main:app --reload
```

### Records API

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/records` | Save a record |
| `GET` | `/api/records` | List records |
| `GET` | `/api/records/{id}` | Fetch a record |
| `PUT` | `/api/records/{id}` | Update record title |
| `DELETE` | `/api/records/{id}` | Delete a record |
| `POST` | `/api/records/{id}/rerun` | Re-run the stored input |
```

- [ ] **Step 2: Verify**

Preview README renders correctly.

- [ ] **Step 3: Commit**

```bash
git add README.md
git commit -m "docs: add storage and records API setup instructions"
```


## Verification Summary

Final verification steps after all tasks complete:

- [ ] All Python tests pass: `uv run pytest`
- [ ] All API tests pass: `uv run --package lc-translator-api pytest packages/lc-translator-api/tests`
- [ ] React build succeeds: `pnpm --filter web build`
- [ ] Alembic migration applies cleanly:
  ```bash
  docker compose up -d db
  export LC_TRANSLATOR_DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/lc_translator
  uv run --package lc-translator-api alembic upgrade head
  ```
- [ ] API starts clean with Postgres:
  ```bash
  uv run --package lc-translator-api uvicorn lc_translator_api.main:app --reload
  curl http://localhost:8000/api/health
  ```
- [ ] End-to-end feature works:
  1. Start API and React dev servers (`pnpm run dev` or `./scripts/run-dev.sh` after updating env for Postgres).
  2. Generate an LC, click **Save**, confirm `201` response.
  3. Navigate to **Records**, see the saved record.
  4. Translate an MT700, click **Save**, confirm it appears in the list.
  5. Refresh the page; records persist.
