from __future__ import annotations

from pathlib import Path

from amelie_md.core.frontmatter import parse_frontmatter
from amelie_md.core.metadata import format_frontmatter, infer_metadata
from amelie_md.core.normalizer import normalize_headings
from amelie_md.core.text_cleaner import repair_text_encoding


def normalize_markdown(
    markdown_text: str,
    input_path: Path | None = None,
    repair_encoding: bool = True,
) -> str:
    if repair_encoding:
        markdown_text = repair_text_encoding(markdown_text)

    metadata, content = parse_frontmatter(markdown_text)

    inferred_metadata = infer_metadata(metadata, input_path=input_path)
    normalized_content = normalize_headings(content).strip()

    return f"{format_frontmatter(inferred_metadata)}\n\n{normalized_content}\n"