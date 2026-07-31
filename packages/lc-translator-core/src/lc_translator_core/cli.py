"""Command-line interface for lc-translator."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer

from lc_translator_core import __version__
from lc_translator_core.generator import generate_lc
from lc_translator_core.mapping import map_lc_to_tsrv001
from lc_translator_core.mt700 import Mt700Parser, Mt700Serializer, Mt700Validator
from lc_translator_core.mx import Tsrv001Generator
from lc_translator_core.validation import XsdValidator

app = typer.Typer(help="MT700 to tsrv.001 Letter of Credit translator")


@app.command()
def generate(
    seed: Optional[int] = typer.Option(None, "--seed", help="Random seed for reproducible output"),
    strict: bool = typer.Option(False, "--strict", help="Fail on parser warnings"),
) -> None:
    """Generate an LC, emit MT700 and MX XML, and validate."""
    lc = generate_lc(seed=seed)
    mt_text = Mt700Serializer().serialize(lc)
    mt_report = Mt700Validator().validate(mt_text)

    parse_result = Mt700Parser().parse(mt_text)
    if strict and (parse_result.errors or parse_result.warnings):
        raise typer.BadParameter(
            f"Strict parse failures: {parse_result.errors + parse_result.warnings}"
        )
    if not parse_result.ok():
        typer.secho(f"Parse errors: {parse_result.errors}", fg=typer.colors.RED)
        raise typer.Exit(code=1)
    assert parse_result.lc is not None

    mapped = map_lc_to_tsrv001(parse_result.lc)
    xml = Tsrv001Generator().generate(mapped)

    xsd_validator = XsdValidator()
    if xsd_validator.is_available():
        xsd_validator.validate(xml)
        typer.secho("XSD validation: PASSED", fg=typer.colors.GREEN)
    else:
        typer.secho("XSD validation: SKIPPED (no schema found)", fg=typer.colors.YELLOW)

    typer.echo("--- MT700 ---")
    typer.echo(mt_text)
    typer.echo("\n--- MT700 validation ---")
    typer.echo(f"Valid: {mt_report.valid}")
    if mt_report.warnings:
        typer.echo(f"Warnings: {mt_report.warnings}")
    if mt_report.errors:
        typer.echo(f"Errors: {mt_report.errors}")

    typer.echo("\n--- MX (tsrv.001) ---")
    typer.echo(xml)


@app.command()
def mt_to_mx(
    file: Path = typer.Argument(..., help="Path to MT700 text file", exists=True),
) -> None:
    """Read MT700 from file, translate to MX XML, and print."""
    mt_text = file.read_text()
    result = Mt700Parser().parse(mt_text)
    if not result.ok():
        typer.secho(f"Parse failed: {result.errors}", fg=typer.colors.RED)
        raise typer.Exit(code=1)
    assert result.lc is not None
    mapped = map_lc_to_tsrv001(result.lc)
    xml = Tsrv001Generator().generate(mapped)
    typer.echo(xml)


@app.command()
def validate_mt(
    file: Path = typer.Argument(..., help="Path to MT700 text file", exists=True),
) -> None:
    """Validate MT700 structure."""
    mt_text = file.read_text()
    report = Mt700Validator().validate(mt_text)
    if report.valid:
        typer.secho("MT700 structure: VALID", fg=typer.colors.GREEN)
    else:
        typer.secho("MT700 structure: INVALID", fg=typer.colors.RED)
        for err in report.errors:
            typer.echo(f"  ERROR: {err}")
        raise typer.Exit(code=1)


@app.command()
def validate_mx(
    file: Path = typer.Argument(..., help="Path to MX XML file", exists=True),
    xsd_path: Optional[Path] = typer.Option(None, "--xsd", help="Path to tsrv.001 XSD"),
) -> None:
    """Validate MX XML against the tsrv.001 XSD."""
    xml_text = file.read_text()
    validator = XsdValidator(xsd_path=xsd_path)
    if not validator.is_available():
        typer.secho(
            "No XSD schema available. Set LC_TRANSLATOR_XSD_PATH or run scripts/fetch_xsd.py",
            fg=typer.colors.YELLOW,
        )
        raise typer.Exit(code=1)
    validator.validate(xml_text)
    typer.secho("MX XSD validation: PASSED", fg=typer.colors.GREEN)


@app.command()
def version() -> None:
    """Print version."""
    typer.echo(__version__)
