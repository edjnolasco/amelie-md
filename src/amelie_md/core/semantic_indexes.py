from __future__ import annotations

from typing import Any


INDEXABLE_TYPES = {"figure", "definition"}


def build_semantic_index(blocks: list[Any], block_type: str) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []

    for block in blocks:
        if not isinstance(block, dict):
            continue

        if str(block.get("type", "")).strip() != block_type:
            continue

        label = str(block.get("label", "")).strip()
        title = str(block.get("title", "")).strip()
        identifier = str(block.get("id", "")).strip()

        if not label and not title:
            continue

        items.append(
            {
                "label": label,
                "title": title,
                "id": identifier,
            }
        )

    return items


def inject_semantic_indexes(blocks: list[Any]) -> list[Any]:
    figures = build_semantic_index(blocks, "figure")
    definitions = build_semantic_index(blocks, "definition")

    injected: list[Any] = []

    for block in blocks:
        if not isinstance(block, dict):
            injected.append(block)
            continue

        block_type = str(block.get("type", "")).strip()
        text = str(block.get("text", "")).strip()

        if block_type == "paragraph" and text == "[[LIST_OF_FIGURES]]":
            injected.append(
                {
                    "type": "semantic_index",
                    "kind": "figures",
                    "title": "List of Figures",
                    "items": figures,
                }
            )
            continue

        if block_type == "paragraph" and text == "[[LIST_OF_DEFINITIONS]]":
            injected.append(
                {
                    "type": "semantic_index",
                    "kind": "definitions",
                    "title": "List of Definitions",
                    "items": definitions,
                }
            )
            continue

        injected.append(block)

    return injected
