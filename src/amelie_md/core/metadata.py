from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any


def infer_metadata(metadata: dict[str, Any], input_path: Path | None = None) -> dict[str, Any]:
    title = metadata.get("title")

    if not title and input_path:
        title = input_path.stem.replace("_", " ").replace("-", " ").title()

    return {
        "title": title or "Documento Amelie",
        "subtitle": metadata.get("subtitle") or "",
        "author": metadata.get("author") or "Edwin José Nolasco",
        "date": str(metadata.get("date") or date.today().isoformat()),
    }


def format_frontmatter(metadata: dict[str, Any]) -> str:
    lines = ["---"]

    for key in ("title", "subtitle", "author", "date"):
        value = metadata.get(key)
        if value:
            lines.append(f'{key}: "{value}"')

    lines.append("---")
    return "\n".join(lines)