"""Records endpoint router."""

from __future__ import annotations

from typing import Optional

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
    source_type: Optional[str] = Query(None),
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
