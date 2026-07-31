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
