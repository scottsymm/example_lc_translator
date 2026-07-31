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
