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
