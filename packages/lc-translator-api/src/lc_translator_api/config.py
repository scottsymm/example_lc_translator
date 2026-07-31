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
