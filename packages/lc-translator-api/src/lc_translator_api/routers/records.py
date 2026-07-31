"""Records endpoint router."""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from lc_translator_api.dependencies import get_db
from lc_translator_api.repositories.record import RecordRepository
from lc_translator_api.schemas.generate import GenerateRequest
from lc_translator_api.schemas.record import (
    RecordCreate,
    RecordOut,
    RecordSummary,
    RecordUpdate,
)
from lc_translator_api.schemas.translate import TranslateRequest

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


@router.post("/records/{record_id}/rerun")
def rerun_record(record_id: str, repo: RecordRepository = Depends(_get_repository)) -> Any:
    """Re-run the stored input through the engine and return fresh output."""
    record = repo.get(record_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Record not found")

    if record.source_type == "generated":
        from lc_translator_api.routers.generate import generate_endpoint

        if record.generated_seed is None or record.generated_strict is None:
            raise HTTPException(status_code=400, detail="Record missing generation parameters")
        return generate_endpoint(GenerateRequest(seed=record.generated_seed, strict=record.generated_strict))

    if record.source_type in {"translated", "validated"}:
        from lc_translator_api.routers.translate import translate_endpoint

        if record.mt700_input is None:
            raise HTTPException(status_code=400, detail="Record missing MT700 input")
        return translate_endpoint(TranslateRequest(mt700=record.mt700_input))

    raise HTTPException(status_code=400, detail=f"Unsupported source_type: {record.source_type}")
