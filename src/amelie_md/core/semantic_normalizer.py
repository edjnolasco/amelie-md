from __future__ import annotations
import re

from typing import Any


def normalize_semantic_blocks(blocks: list[Any]) -> list[Any]:
    normalized_blocks: list[Any] = []
    index = 0

    while index < len(blocks):
        block = blocks[index]

        if not isinstance(block, dict):
            normalized_blocks.append(block)
            index += 1
            continue

        block_type = str(block.get("type", "")).strip()
        text = str(block.get("text", "")).strip()

        if block_type != "paragraph" or not text.startswith(":::"):
            normalized_blocks.append(block)
            index += 1
            continue

        marker = text[3:].strip()

        if not marker:
            normalized_blocks.append(block)
            index += 1
            continue

        kind, title, identifier = parse_admonition_marker(marker)
        content_lines: list[str] = []
        index += 1

        while index < len(blocks):
            current_block = blocks[index]

            if not isinstance(current_block, dict):
                index += 1
                continue

            current_text = str(current_block.get("text", "")).strip()

            if current_text == ":::":
                index += 1
                break

            if current_text:
                content_lines.append(current_text)

            index += 1

        content = "\n".join(content_lines).strip()

        if content:
            normalized_blocks.append(
                {
                    "type": semantic_block_type(kind),
                    "kind": kind,
                    "id": identifier,
                    "title": title,
                    "text": content,
                }
            )

    return normalized_blocks


def parse_admonition_marker(marker: str) -> tuple[str, str, str]:
    marker = marker.strip()

    if not marker:
        return "note", "Note", ""

    parts = marker.split(maxsplit=1)

    kind = parts[0].strip().lower()
    remaining = parts[1].strip() if len(parts) > 1 else ""

    if kind in {"definition", "figure"}:
        remaining_parts = remaining.split(maxsplit=1)

        if (
            len(remaining_parts) == 2
            and re.fullmatch(r"[A-Za-z0-9]+(?:[-_.:][A-Za-z0-9]+)+", remaining_parts[0])
        ):
            identifier, title = remaining_parts
            return kind, title.strip(), identifier.strip()

        return kind, remaining.strip() or kind.title(), ""

    return kind, remaining.strip() or kind.title(), ""



def semantic_block_type(kind: str) -> str:
    if kind in {"definition", "quote", "figure"}:
        return kind

    return "admonition"
