from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


BlockType = Literal["paragraph", "heading", "table", "code", "list_item"]


@dataclass(frozen=True)
class DocumentBlock:
    type: BlockType
    text: str = ""
    level: int | None = None
    rows: list[list[str]] | None = None
    language: str | None = None
    ordered: bool = False
    indent: int = 0


@dataclass(frozen=True)
class AmelieDocument:
    blocks: list[DocumentBlock] = field(default_factory=list)

    def to_markdown(self) -> str:
        parts: list[str] = []
        i = 0

        while i < len(self.blocks):
            block = self.blocks[i]

            if block.type == "list_item":
                ordered = block.ordered
                list_items: list[DocumentBlock] = []

                while (
                    i < len(self.blocks)
                    and self.blocks[i].type == "list_item"
                    and self.blocks[i].ordered == ordered
                ):
                    list_items.append(self.blocks[i])
                    i += 1

                for item in list_items:
                    marker = "1." if item.ordered else "-"
                    spaces = "  " * max(item.indent, 0)
                    text = item.text.strip()

                    if text:
                        parts.append(f"{spaces}{marker} {text}")

                parts.append("")
                continue

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
                    i += 1
                    continue

                header = block.rows[0]
                body = block.rows[1:]

                parts.append("| " + " | ".join(header) + " |")
                parts.append("| " + " | ".join(["---"] * len(header)) + " |")

                for row in body:
                    normalized = row + [""] * (len(header) - len(row))
                    parts.append("| " + " | ".join(normalized[: len(header)]) + " |")

            parts.append("")
            i += 1

        return "\n".join(parts).strip() + "\n"