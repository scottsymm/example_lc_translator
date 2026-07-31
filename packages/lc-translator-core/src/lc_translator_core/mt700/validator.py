"""MT700 structural validation."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

_TAG_PATTERN = re.compile(r"^:(\d{2}[A-Z]?):(.*)$")
_MT700_REQUIRED_TAGS: set[str] = {"20", "31C", "31D", "50", "59", "32B"}
_LINE_LIMIT = 65
_ADDRESS_LINE_LIMIT = 35


@dataclass
class Mt700ValidationReport:
    """Report of structural checks on an MT700 message."""

    valid: bool = True
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def add_error(self, message: str) -> None:
        """Record an error and mark the report invalid."""
        self.errors.append(message)
        self.valid = False

    def add_warning(self, message: str) -> None:
        """Record a warning."""
        self.warnings.append(message)


class Mt700Validator:
    """Validate raw MT700 text structure."""

    def validate(self, text: str) -> Mt700ValidationReport:
        """Check line lengths and required tags."""
        report = Mt700ValidationReport()
        lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
        seen_tags: set[str] = set()
        in_address_tag = False
        address_limit_window: set[str] = {"50", "59"}

        for idx, raw_line in enumerate(lines, start=1):
            if not raw_line.strip():
                continue
            if len(raw_line) > _LINE_LIMIT:
                report.add_error(f"Line {idx} exceeds {_LINE_LIMIT} characters")

            match = _TAG_PATTERN.match(raw_line)
            if match:
                tag, _value = match.groups()
                seen_tags.add(tag)
                in_address_tag = tag in address_limit_window
            elif in_address_tag and len(raw_line) > _ADDRESS_LINE_LIMIT:
                report.add_warning(
                    f"Line {idx} within address tag exceeds {_ADDRESS_LINE_LIMIT} characters"
                )

        missing = _MT700_REQUIRED_TAGS - seen_tags
        for tag in sorted(missing):
            report.add_error(f"Required tag :{tag}: is missing")

        return report
