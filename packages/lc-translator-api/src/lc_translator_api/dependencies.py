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
