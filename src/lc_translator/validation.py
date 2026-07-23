"""XSD loading, caching, and XML validation."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from lxml import etree

from lc_translator.exceptions import XsdValidationError

_DEFAULT_CACHE_DIR = Path.home() / ".cache" / "lc-translator" / "xsd"


def _xsd_path_from_env() -> Optional[Path]:
    env = os.environ.get("LC_TRANSLATOR_XSD_PATH")
    return Path(env) if env else None


def _tsrv001_builtin_path() -> Optional[Path]:
    here = Path(__file__).resolve().parent
    candidate = here / "schemas" / "tsrv.001.001.01.xsd"
    return candidate if candidate.exists() else None


def _find_xsd_path() -> Optional[Path]:
    return _xsd_path_from_env() or _tsrv001_builtin_path()


class XsdValidator:
    """Validate tsrv.001 XML against its XSD schema."""

    def __init__(self, xsd_path: Optional[Path] = None) -> None:
        """Initialize validator.

        If xsd_path is provided, it is used directly. Otherwise the validator
        looks at LC_TRANSLATOR_XSD_PATH, then the built-in schema directory.
        """
        self.xsd_path = xsd_path or _find_xsd_path()
        self._schema: Optional[etree.XMLSchema] = None

    def is_available(self) -> bool:
        """Return True if an XSD schema file was located."""
        return self.xsd_path is not None and self.xsd_path.exists()

    def _load_schema(self) -> etree.XMLSchema:
        if self._schema is None:
            if self.xsd_path is None or not self.xsd_path.exists():
                raise XsdValidationError("XSD schema not found")
            tree = etree.parse(str(self.xsd_path))
            self._schema = etree.XMLSchema(tree)
        return self._schema

    def validate(self, xml_text: str) -> None:
        """Validate XML text against the XSD."""
        schema = self._load_schema()
        try:
            root = etree.fromstring(xml_text.encode("utf-8"))
            schema.assertValid(root)
        except etree.DocumentInvalid as exc:
            raise XsdValidationError(f"XSD validation failed: {exc}") from exc
        except etree.XMLSyntaxError as exc:
            raise XsdValidationError(f"Malformed XML: {exc}") from exc
