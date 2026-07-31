"""Pydantic schemas for stored LC records."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class ValidationResult(BaseModel):
    """Structured validation output."""

    mt700_valid: Optional[bool] = None
    mt700_errors: list[str] = []
    mt700_warnings: list[str] = []
    mx_valid: Optional[bool] = None
    mx_errors: list[str] = []


class RecordCreate(BaseModel):
    """Payload for creating a record."""

    title: Optional[str] = Field(None, description="Optional human-readable title")
    source_type: str = Field(..., description="One of generated, translated, validated")
    mt700_input: Optional[str] = Field(None, description="MT700 input text")
    generated_seed: Optional[int] = Field(None, description="Seed used for generation")
    generated_strict: Optional[bool] = Field(None, description="Strict flag used for generation")
    mx_xml: Optional[str] = Field(None, description="Generated MX XML")
    validation_result: Optional[ValidationResult] = None
    lc_model: Optional[dict[str, Any]] = None


class RecordUpdate(BaseModel):
    """Payload for updating a record."""

    title: Optional[str] = None


class RecordOut(BaseModel):
    """Full record response."""

    id: str
    title: str
    source_type: str
    created_at: datetime
    updated_at: datetime
    mt700_input: Optional[str]
    generated_seed: Optional[int]
    generated_strict: Optional[bool]
    mx_xml: Optional[str]
    validation_result: Optional[ValidationResult]
    lc_model: Optional[dict[str, Any]]

    model_config = {"from_attributes": True}


class RecordSummary(BaseModel):
    """Lightweight record list item."""

    id: str
    title: str
    source_type: str
    created_at: datetime

    model_config = {"from_attributes": True}
