"""Shared FastAPI dependencies."""

from __future__ import annotations

from typing import Any

from fastapi import Request

from lc_translator_api.config import Settings, get_settings


def get_settings_dependency() -> Settings:
    """Return application settings."""
    return get_settings()


def get_xsd_schema(request: Request) -> Any:
    """Return the preloaded XSD schema from app state."""
    return request.app.state.xsd_schema
