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
