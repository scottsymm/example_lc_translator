"""Generate endpoint router."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from lc_translator_core.generator import generate_lc
from lc_translator_core.mapping import map_lc_to_tsrv001
from lc_translator_core.mt700 import Mt700Parser, Mt700Serializer, Mt700Validator
from lc_translator_core.mx import Tsrv001Generator
from lc_translator_core.validation import XsdValidationError, XsdValidator

from lc_translator_api.schemas.generate import GenerateRequest, GenerateResponse

router = APIRouter(tags=["generate"])


@router.post("/generate", response_model=GenerateResponse)
def generate_endpoint(request: GenerateRequest) -> GenerateResponse:
    """Generate a fake LC and run the full MT700 -> MX pipeline."""
    lc = generate_lc(seed=request.seed)
    mt_text = Mt700Serializer().serialize(lc)

    mt_report = Mt700Validator().validate(mt_text)

    parse_result = Mt700Parser().parse(mt_text)
    if parse_result.errors:
        raise HTTPException(status_code=400, detail={"errors": parse_result.errors})
    if request.strict and parse_result.warnings:
        raise HTTPException(status_code=400, detail={"warnings": parse_result.warnings})
    if parse_result.lc is None:
        raise HTTPException(status_code=400, detail={"errors": ["Failed to parse MT700"]})

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

    return GenerateResponse(
        lc_number=lc.lc_number,
        mt700=mt_text,
        mx_xml=mx_xml,
        mt700_valid=mt_report.valid,
        mt700_errors=mt_report.errors,
        mt700_warnings=mt_report.warnings,
        mx_valid=mx_valid,
        mx_errors=mx_errors,
    )
