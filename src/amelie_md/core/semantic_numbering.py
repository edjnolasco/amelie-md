from __future__ import annotations

from typing import Any


NUMBERED_TYPES = {"definition", "figure"}


def apply_semantic_numbering(blocks: list[Any]) -> list[Any]:
    counters: dict[str, int] = {}
    numbered_blocks: list[Any] = []

    for block in blocks:
        if not isinstance(block, dict):
            numbered_blocks.append(block)
            continue

        block_type = str(block.get("type", "")).strip()

        if block_type not in NUMBERED_TYPES:
            numbered_blocks.append(block)
            continue

        counters[block_type] = counters.get(block_type, 0) + 1

        clean_block = dict(block)
        clean_block["number"] = counters[block_type]
        clean_block["label"] = semantic_label(block_type, counters[block_type])

        numbered_blocks.append(clean_block)

    return numbered_blocks


def semantic_label(block_type: str, number: int) -> str:
    labels = {
        "definition": "Definition",
        "figure": "Figure",
    }

    prefix = labels.get(block_type, block_type.title())
    return f"{prefix} {number}"
