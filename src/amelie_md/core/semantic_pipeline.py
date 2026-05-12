from __future__ import annotations

from typing import Any

from amelie_md.core.semantic_indexes import inject_semantic_indexes
from amelie_md.core.semantic_normalizer import normalize_semantic_blocks
from amelie_md.core.semantic_numbering import apply_semantic_numbering
from amelie_md.core.semantic_references import apply_semantic_references


def prepare_semantic_blocks(
    blocks: list[Any],
    *,
    html_links: bool = False,
    inject_indexes: bool = True,
) -> list[Any]:
    normalized_blocks = normalize_semantic_blocks(blocks)
    numbered_blocks = apply_semantic_numbering(normalized_blocks)
    referenced_blocks = apply_semantic_references(
        numbered_blocks,
        html_links=html_links,
    )

    if not inject_indexes:
        return referenced_blocks

    return inject_semantic_indexes(referenced_blocks)
