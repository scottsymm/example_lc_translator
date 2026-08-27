"""CLI helper to run Alembic migrations."""

from __future__ import annotations

from alembic import command
from alembic.config import Config

from lc_translator_api.config import get_settings


def main() -> None:
    """Run Alembic upgrade to the latest revision."""
    settings = get_settings()
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", settings.database_url)
    command.upgrade(alembic_cfg, "head")


if __name__ == "__main__":
    main()
