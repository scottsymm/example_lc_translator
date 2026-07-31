"""Pydantic schemas for the generate endpoint."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class GenerateRequest(BaseModel):
    """Optional parameters for LC generation."""

    seed: Optional[int] = Field(None, description="Random seed for reproducible output")
    strict: bool = Field(False, description="Fail on parser warnings")


class GenerateResponse(BaseModel):
    """Full pipeline output for a generated LC."""

    lc_number: str
    mt700: str
    mx_xml: str
    mt700_valid: bool
    mt700_errors: list[str]
    mt700_warnings: list[str]
    mx_valid: Optional[bool] = None
    mx_errors: list[str] = []
