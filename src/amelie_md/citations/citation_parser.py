from __future__ import annotations

import re
from typing import Any

from amelie_md.citations.citation_registry import format_author_year


CITATION_PATTERN = re.compile(r"\[@([A-Za-z0-9_.:-]+)\]")


def resolve_citations(
    text: str,
    registry: dict[str, dict[str, Any]],
) -> str:
    def replace(match: re.Match[str]) -> str:
        key = match.group(1)
        entry = registry.get(key)

        if not entry:
            return match.group(0)

        return format_author_year(entry)

    return CITATION_PATTERN.sub(replace, text)


def apply_citations_to_blocks(
    blocks: list[Any],
    registry: dict[str, dict[str, Any]],
) -> list[Any]:
    resolved_blocks: list[Any] = []

    for block in blocks:
        if not isinstance(block, dict):
            resolved_blocks.append(block)
            continue

        clean_block = dict(block)

        for field in ("text", "title"):
            value = clean_block.get(field)

            if isinstance(value, str):
                clean_block[field] = resolve_citations(value, registry)

        resolved_blocks.append(clean_block)

    return resolved_blocks
