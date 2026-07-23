"""End-to-end pipeline integration test."""

from lc_translator.generator import generate_lc
from lc_translator.mapping import map_lc_to_tsrv001
from lc_translator.mt700 import Mt700Parser, Mt700Serializer, Mt700Validator
from lc_translator.mx import Tsrv001Generator
from lc_translator.validation import XsdValidator


def test_full_pipeline_with_deterministic_seed() -> None:
    lc = generate_lc(seed=42)
    mt_text = Mt700Serializer().serialize(lc)

    mt_report = Mt700Validator().validate(mt_text)
    assert mt_report.valid, mt_report.errors

    parse_result = Mt700Parser().parse(mt_text)
    assert parse_result.ok(), parse_result.errors
    assert parse_result.lc is not None

    mapped = map_lc_to_tsrv001(parse_result.lc)
    xml = Tsrv001Generator().generate(mapped)
    assert "UdrtkgIssnc" in xml
    assert lc.lc_number in xml


def test_generated_xml_validates_against_bundled_schema() -> None:
    lc = generate_lc(seed=42)
    mt_text = Mt700Serializer().serialize(lc)
    parse_result = Mt700Parser().parse(mt_text)
    assert parse_result.ok(), parse_result.errors
    assert parse_result.lc is not None

    mapped = map_lc_to_tsrv001(parse_result.lc)
    xml = Tsrv001Generator().generate(mapped)

    validator = XsdValidator()
    assert validator.is_available(), "Bundled XSD schema not found"
    validator.validate(xml)
