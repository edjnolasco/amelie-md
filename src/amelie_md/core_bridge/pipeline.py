from __future__ import annotations

import re
from typing import Any

from amelie_core.pipeline.document_pipeline import process_document

from amelie_md.document import AmelieDocument


FENCE_RE = re.compile(r"```(?P<lang>[a-zA-Z0-9_-]*)\n(?P<code>.*?)(?:\n```|$)", re.DOTALL)
BULLET_RE = re.compile(r"^(?P<indent>\s*)[-*+]\s+(?P<text>.+)$")
ORDERED_RE = re.compile(r"^(?P<indent>\s*)\d+(?:\.\d+)*\.?\s+(?P<text>.+)$")


def process_markdown_with_core(
    markdown_text: str,
    style_text: str | None = None,
) -> dict[str, Any]:
    """
    Bridge between amelie-core and amelie-md.

    Converts the core document model into an AmelieDocument-compatible
    block structure for v1.2 exporters.
    """

    result = process_document(markdown_text, style_text)

    if not isinstance(result, dict):
        raise TypeError("Core pipeline must return a dictionary result.")

    core_document = result.get("document")

    if core_document is None:
        raise ValueError("Core pipeline did not return a document.")

    blocks = _core_document_to_blocks(core_document)

    return {
        "document": AmelieDocument(blocks=blocks),
        "validation": result.get("validation"),
        "style": result.get("style"),
    }


def _core_document_to_blocks(core_document: Any) -> list[dict[str, Any]]:
    blocks: list[dict[str, Any]] = []

    sections = getattr(core_document, "sections", None)

    if not sections:
        raw = getattr(core_document, "raw", "")
        return _content_to_blocks(str(raw)) if raw else []

    for section in sections:
        title = str(getattr(section, "title", "") or "").strip()
        level = int(getattr(section, "level", 1) or 1)
        content = str(getattr(section, "content", "") or "")

        if title:
            blocks.append(
                {
                    "type": "heading",
                    "level": max(1, min(level, 6)),
                    "text": _clean_heading_text(title),
                }
            )

        blocks.extend(_content_to_blocks(content))

    return _remove_empty_blocks(blocks)


def _content_to_blocks(content: str) -> list[dict[str, Any]]:
    blocks: list[dict[str, Any]] = []

    if not content.strip():
        return blocks

    remaining = content

    while remaining:
        fence_match = FENCE_RE.search(remaining)

        if not fence_match:
            blocks.extend(_markdown_chunk_to_blocks(remaining))
            break

        before = remaining[: fence_match.start()]
        code = fence_match.group("code")
        language = fence_match.group("lang") or None

        blocks.extend(_markdown_chunk_to_blocks(before))

        blocks.append(
            {
                "type": "code",
                "code": code.rstrip("\n"),
                "language": language,
            }
        )

        remaining = remaining[fence_match.end() :]

    return _remove_empty_blocks(blocks)


def _markdown_chunk_to_blocks(chunk: str) -> list[dict[str, Any]]:
    blocks: list[dict[str, Any]] = []
    lines = chunk.splitlines()
    index = 0

    paragraph_lines: list[str] = []

    def flush_paragraph() -> None:
        nonlocal paragraph_lines

        if not paragraph_lines:
            return

        text = " ".join(line.strip() for line in paragraph_lines if line.strip()).strip()

        if text:
            if text == "[[TOC]]":
                blocks.append({"type": "toc"})
            else:
                blocks.append({"type": "paragraph", "text": text})

        paragraph_lines = []

    while index < len(lines):
        line = lines[index]
        stripped = line.strip()

        if not stripped:
            flush_paragraph()
            index += 1
            continue

        if stripped == "---":
            flush_paragraph()
            index += 1
            continue

        if _looks_like_table_start(lines, index):
            flush_paragraph()
            table_rows, index = _consume_markdown_table(lines, index)
            if table_rows:
                blocks.append({"type": "table", "rows": table_rows})
            continue

        bullet_match = BULLET_RE.match(line)
        if bullet_match:
            flush_paragraph()
            blocks.append(
                {
                    "type": "list_item",
                    "text": bullet_match.group("text").strip(),
                    "level": _indent_to_level(bullet_match.group("indent")),
                    "ordered": False,
                }
            )
            index += 1
            continue

        ordered_match = ORDERED_RE.match(line)
        if ordered_match:
            flush_paragraph()
            blocks.append(
                {
                    "type": "list_item",
                    "text": ordered_match.group("text").strip(),
                    "level": _indent_to_level(ordered_match.group("indent")),
                    "ordered": True,
                }
            )
            index += 1
            continue

        paragraph_lines.append(line)
        index += 1

    flush_paragraph()
    return _remove_empty_blocks(blocks)


def _looks_like_table_start(lines: list[str], index: int) -> bool:
    if index + 1 >= len(lines):
        return False

    header = lines[index].strip()
    separator = lines[index + 1].strip()

    return (
        header.startswith("|")
        and header.endswith("|")
        and separator.startswith("|")
        and separator.endswith("|")
        and set(separator.replace("|", "").replace(":", "").replace("-", "").strip()) == set()
    )


def _consume_markdown_table(
    lines: list[str],
    start_index: int,
) -> tuple[list[list[str]], int]:
    table_lines: list[str] = []
    index = start_index

    while index < len(lines):
        stripped = lines[index].strip()

        if not stripped.startswith("|") or not stripped.endswith("|"):
            break

        table_lines.append(stripped)
        index += 1

    if len(table_lines) < 2:
        return [], index

    rows: list[list[str]] = []

    for line_index, line in enumerate(table_lines):
        if line_index == 1:
            continue

        cells = [cell.strip() for cell in line.strip("|").split("|")]
        rows.append(cells)

    return rows, index


def _indent_to_level(indent: str) -> int:
    expanded = indent.replace("\t", "    ")
    return max(len(expanded) // 2, 0)


def _clean_heading_text(text: str) -> str:
    return re.sub(
        r"^\s*(?:\d+(?:\.\d+)*\.?|[IVXLCDM]+\.|[A-Z]\.)\s+",
        "",
        text,
        count=1,
        flags=re.IGNORECASE,
    ).strip()


def _remove_empty_blocks(blocks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    cleaned: list[dict[str, Any]] = []

    for block in blocks:
        block_type = str(block.get("type", "")).strip()

        if not block_type:
            continue

        if block_type in {"heading", "paragraph", "list_item"}:
            text = str(block.get("text", "")).strip()
            if not text:
                continue
            block["text"] = text

        if block_type == "code":
            code = str(block.get("code", "")).rstrip()
            if not code:
                continue
            block["code"] = code

        if block_type == "table":
            rows = block.get("rows") or []
            if not rows:
                continue
            block["rows"] = rows

        cleaned.append(block)

    return cleaned
