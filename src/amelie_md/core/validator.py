from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from amelie_md.core.frontmatter import parse_frontmatter


HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    severity: str
    message: str


@dataclass(frozen=True)
class ValidationReport:
    issues: list[ValidationIssue]

    @property
    def has_errors(self) -> bool:
        return any(issue.severity == "error" for issue in self.issues)

    @property
    def has_warnings(self) -> bool:
        return any(issue.severity == "warning" for issue in self.issues)


def validate_markdown(markdown_text: str, profile: str = "technical") -> ValidationReport:
    issues: list[ValidationIssue] = []

    metadata, content = parse_frontmatter(markdown_text)

    if not content.strip():
        issues.append(
            ValidationIssue(
                code="empty_document",
                severity="error",
                message="The document has no Markdown content.",
            )
        )

    _validate_metadata(metadata, issues)
    _validate_headings(content, issues)

    if profile == "academic":
        _validate_academic_sections(content, issues)

    return ValidationReport(issues=issues)

def _validate_academic_sections(content: str, issues: list[ValidationIssue]) -> None:
    normalized = content.lower()

    required_sections = {
        "introducción": ["# introducción", "## introducción"],
        "conclusiones": ["# conclusiones", "## conclusiones", "# conclusión", "## conclusión"],
    }

    for section_name, candidates in required_sections.items():
        if not any(candidate in normalized for candidate in candidates):
            issues.append(
                ValidationIssue(
                    code=f"missing_section_{section_name}",
                    severity="warning",
                    message=f"Required section not found (academic profile): {section_name}.",
                )
            )

def _validate_metadata(metadata: dict[str, Any], issues: list[ValidationIssue]) -> None:
    if not metadata.get("title"):
        issues.append(
            ValidationIssue(
                code="missing_title",
                severity="warning",
                message="Missing metadata field: title.",
            )
        )

    if not metadata.get("author"):
        issues.append(
            ValidationIssue(
                code="missing_author",
                severity="warning",
                message="Missing metadata field: author.",
            )
        )

    if not metadata.get("date"):
        issues.append(
            ValidationIssue(
                code="missing_date",
                severity="warning",
                message="Missing metadata field: date.",
            )
        )


def _validate_headings(content: str, issues: list[ValidationIssue]) -> None:
    headings = [(len(match.group(1)), match.group(2).strip()) for match in HEADING_PATTERN.finditer(content)]

    if not headings:
        issues.append(
            ValidationIssue(
                code="missing_headings",
                severity="warning",
                message="The document has no headings.",
            )
        )
        return

    last_level = 0

    for level, text in headings:
        if last_level and level > last_level + 1:
            issues.append(
                ValidationIssue(
                    code="heading_jump",
                    severity="warning",
                    message=f"Heading hierarchy jump detected near: {text}",
                )
            )

        last_level = level
