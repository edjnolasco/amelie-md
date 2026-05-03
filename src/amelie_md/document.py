from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


BlockType = Literal["paragraph", "heading", "table", "code"]


@dataclass(frozen=True)
class DocumentBlock:
    type: BlockType
    text: str = ""
    level: int | None = None
    rows: list[list[str]] | None = None
    language: str | None = None


@dataclass(frozen=True)
class AmelieDocument:
    blocks: list[DocumentBlock] = field(default_factory=list)

    def to_markdown(self) -> str:
        parts: list[str] = []

        for block in self.blocks:
            if block.type == "heading":
                level = block.level or 1
                parts.append(f"{'#' * level} {block.text.strip()}")

            elif block.type == "paragraph":
                if block.text.strip():
                    parts.append(block.text.strip())

            elif block.type == "code":
                language = block.language or ""
                parts.append(f"```{language}\n{block.text.rstrip()}\n```")

            elif block.type == "table":
                if not block.rows:
                    continue

                header = block.rows[0]
                body = block.rows[1:]

                parts.append("| " + " | ".join(header) + " |")
                parts.append("| " + " | ".join(["---"] * len(header)) + " |")

                for row in body:
                    normalized = row + [""] * (len(header) - len(row))
                    parts.append("| " + " | ".join(normalized[: len(header)]) + " |")

            parts.append("")

        return "\n".join(parts).strip() + "\n"