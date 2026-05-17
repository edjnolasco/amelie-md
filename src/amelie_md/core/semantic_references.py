from __future__ import annotations

import re
from typing import Any

from amelie_md.renderers.components.html_blocks import render_semantic_reference


REF_PATTERN = re.compile(r"\{\{ref:([A-Za-z0-9_.:-]+)\}\}")


def apply_semantic_references(
    blocks: list[Any],
    *,
    html_links: bool = False,
) -> list[Any]:
    reference_map = build_reference_map(blocks)
    resolved_blocks: list[Any] = []

    for block in blocks:
        if not isinstance(block, dict):
            resolved_blocks.append(block)
            continue

        clean_block = dict(block)

        for field in ("text", "title"):
            value = clean_block.get(field)

            if isinstance(value, str):
                clean_block[field] = resolve_references(
                    value,
                    reference_map,
                    html_links=html_links,
                )

        resolved_blocks.append(clean_block)

    return resolved_blocks


def build_reference_map(blocks: list[Any]) -> dict[str, str]:
    references: dict[str, str] = {}

    for block in blocks:
        if not isinstance(block, dict):
            continue

        identifier = str(block.get("id", "")).strip()
        label = str(block.get("label", "")).strip()

        if identifier and label:
            references[identifier] = label

    return references


def resolve_references(
    text: str,
    reference_map: dict[str, str],
    *,
    html_links: bool = False,
) -> str:
    def replace(match: re.Match[str]) -> str:
        identifier = match.group(1)
        label = reference_map.get(identifier)

        if not label:
            return match.group(0)

        if html_links:
            return render_semantic_reference(identifier, label)

        return label

    return REF_PATTERN.sub(replace, text)
