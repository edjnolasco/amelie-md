from __future__ import annotations

import re
from typing import Any

from amelie_md.citations.citation_registry import format_author_year


CITATION_PATTERN = re.compile(r"\[@([A-Za-z0-9_.:-]+)\]")


def extract_citation_keys(text: str) -> list[str]:
    return CITATION_PATTERN.findall(text)


def collect_cited_keys(blocks: list[Any]) -> list[str]:
    keys: list[str] = []

    for block in blocks:
        if not isinstance(block, dict):
            continue

        for field in ("text", "title"):
            value = block.get(field)

            if not isinstance(value, str):
                continue

            for key in extract_citation_keys(value):
                if key not in keys:
                    keys.append(key)

    return keys


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
