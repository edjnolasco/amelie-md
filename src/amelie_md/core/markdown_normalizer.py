from __future__ import annotations

from pathlib import Path

from amelie_md.core.frontmatter import parse_frontmatter
from amelie_md.core.metadata import format_frontmatter, infer_metadata
from amelie_md.core.normalizer import normalize_headings
from amelie_md.core.text_cleaner import repair_text_encoding

def _wrap_ascii_diagrams(content: str) -> str:
    lines = content.splitlines()
    result: list[str] = []

    diagram_chars = ("│", "─", "▼", "├", "└", "┌", "┐", "┘", "┬", "┴")

    def has_diagram_chars(line: str) -> bool:
        # Ignorar listas normales
        stripped = line.strip()

        if stripped.startswith(("- ", "* ", "+ ")):
            return False

        # Detectar solo caracteres estructurales reales
        diagram_chars = ("│", "─", "├", "└", "┌", "┐", "┘", "┬", "┴", "▼")

        return any(ch in line for ch in diagram_chars)

    def looks_like_heading(line: str) -> bool:
        return line.lstrip().startswith("#")

    i = 0

    while i < len(lines):
        line = lines[i]

        if looks_like_heading(line):
            result.append(line)
            i += 1
            continue

        lookahead = lines[i : i + 12]
        diagram_count = sum(1 for item in lookahead if has_diagram_chars(item))

        if (
            line.strip()
            and diagram_count >= 2
            and not line.strip().startswith("---")
        ):
            block: list[str] = []

            while i < len(lines):
                current = lines[i]

                if looks_like_heading(current):
                    break

                if current.strip() == "":
                    next_lines = lines[i + 1 : i + 6]
                    if not any(has_diagram_chars(item) for item in next_lines):
                        break

                block.append(current)
                i += 1

            result.append("```text")
            result.extend(block)
            result.append("```")
            continue

        result.append(line)
        i += 1

    return "\n".join(result)

def normalize_markdown(
    markdown_text: str,
    input_path: Path | None = None,
    repair_encoding: bool = True,
) -> str:
    if repair_encoding:
        markdown_text = repair_text_encoding(markdown_text)

    metadata, content = parse_frontmatter(markdown_text)

    inferred_metadata = infer_metadata(metadata, input_path=input_path)
    normalized_content = normalize_headings(content)
    normalized_content = _wrap_ascii_diagrams(normalized_content).strip()

    return f"{format_frontmatter(inferred_metadata)}\n\n{normalized_content}\n"