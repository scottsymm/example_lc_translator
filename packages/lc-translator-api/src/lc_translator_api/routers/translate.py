"""Translate endpoint router."""

from __future__ import annotations

from fastapi import APIRouter
from lc_translator_core.mapping import map_lc_to_tsrv001
from lc_translator_core.mt700 import Mt700Parser
from lc_translator_core.mx import Tsrv001Generator
from lc_translator_core.validation import XsdValidationError, XsdValidator

from lc_translator_api.schemas.translate import TranslateRequest, TranslateResponse

router = APIRouter(tags=["translate"])


@router.post("/mt-to-mx", response_model=TranslateResponse)
def mt_to_mx_endpoint(request: TranslateRequest) -> TranslateResponse:
    """Translate a raw MT700 message into MX XML."""
    parse_result = Mt700Parser().parse(request.mt700)
    if not parse_result.ok() or parse_result.lc is None:
        return TranslateResponse(
            mx_xml="",
            warnings=parse_result.warnings,
            errors=parse_result.errors or ["Failed to parse MT700"],
        )

    mapped = map_lc_to_tsrv001(parse_result.lc)
    mx_xml = Tsrv001Generator().generate(mapped)

    mx_valid = None
    mx_errors: list[str] = []
    validator = XsdValidator()
    if validator.is_available():
        try:
            validator.validate(mx_xml)
            mx_valid = True
        except XsdValidationError as exc:
            mx_valid = False
            mx_errors.append(str(exc))

    return TranslateResponse(
        mx_xml=mx_xml,
        warnings=parse_result.warnings,
        errors=[],
        mx_valid=mx_valid,
        mx_errors=mx_errors,
    )
