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
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
