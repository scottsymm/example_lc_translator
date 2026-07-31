"""Pydantic schemas for the translate endpoint."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class TranslateRequest(BaseModel):
    """MT700 text to translate."""

    mt700: str = Field(..., min_length=1, description="Raw MT700 message text")


class TranslateResponse(BaseModel):
    """MX XML translation result."""

    mx_xml: str
    warnings: list[str] = []
    errors: list[str] = []
    mx_valid: Optional[bool] = None
    mx_errors: list[str] = []
