"""Validate endpoints router."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from lc_translator_api.dependencies import get_db
from lc_translator_core.mt700 import Mt700Validator
from lc_translator_core.validation import XsdValidationError, XsdValidator

from lc_translator_api.schemas.validate import (
    ValidateMtRequest,
    ValidateMtResponse,
    ValidateMxRequest,
    ValidateMxResponse,
)

router = APIRouter(tags=["validate"])


@router.post("/validate-mt", response_model=ValidateMtResponse)
def validate_mt_endpoint(request: ValidateMtRequest) -> ValidateMtResponse:
    """Validate MT700 structure."""
    report = Mt700Validator().validate(request.mt700)
    return ValidateMtResponse(
        valid=report.valid,
        errors=report.errors,
        warnings=report.warnings,
    )


@router.post("/validate-mx", response_model=ValidateMxResponse)
def validate_mx_endpoint(request: ValidateMxRequest) -> ValidateMxResponse:
    """Validate MX XML against the bundled tsrv.001 XSD."""
    validator = XsdValidator()
    if not validator.is_available():
        return ValidateMxResponse(
            valid=False,
            errors=["XSD schema not available"],
        )

    try:
        validator.validate(request.mx_xml)
        return ValidateMxResponse(valid=True)
    except XsdValidationError as exc:
        return ValidateMxResponse(valid=False, errors=[str(exc)])


@router.get("/health")
def health_endpoint(db: Session = Depends(get_db)) -> dict[str, str]:
    """Health check, including database connectivity."""
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "ok"}
    except Exception:
        return {"status": "ok", "database": "error"}
