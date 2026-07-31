"""Pydantic schemas for the validate endpoints."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ValidateMtRequest(BaseModel):
    """MT700 text to validate."""

    mt700: str = Field(..., min_length=1, description="Raw MT700 message text")


class ValidateMtResponse(BaseModel):
    """MT700 structure validation result."""

    valid: bool
    errors: list[str] = []
    warnings: list[str] = []


class ValidateMxRequest(BaseModel):
    """MX XML text to validate."""

    mx_xml: str = Field(..., min_length=1, description="MX XML document")


class ValidateMxResponse(BaseModel):
    """MX XSD validation result."""

    valid: bool
    errors: list[str] = []
