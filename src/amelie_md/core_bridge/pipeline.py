from __future__ import annotations

from typing import Any

from amelie_core.pipeline.document_pipeline import process_document

from amelie_md.document import AmelieDocument


def process_markdown_with_core(markdown_text: str, style_text: str | None = None) -> dict[str, Any]:
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
        if raw:
            blocks.append({"type": "paragraph", "text": str(raw)})
        return blocks

    for section in sections:
        title = getattr(section, "title", "")
        level = getattr(section, "level", 1)
        content = getattr(section, "content", "")

        if title:
            blocks.append(
                {
                    "type": "heading",
                    "level": int(level or 1),
                    "text": str(title),
                }
            )

        if content:
            blocks.append(
                {
                    "type": "paragraph",
                    "text": str(content),
                }
            )

    return blocks