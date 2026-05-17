from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_citation_registry(path: str | Path) -> dict[str, dict[str, Any]]:
    citation_path = Path(path)

    if not citation_path.exists():
        return {}

    data = json.loads(citation_path.read_text(encoding="utf-8"))

    if not isinstance(data, dict):
        raise ValueError("Citation registry must be a JSON object.")

    return {
        str(key): value
        for key, value in data.items()
        if isinstance(value, dict)
    }


def format_author_year(entry: dict[str, Any]) -> str:
    authors = str(entry.get("authors", "")).strip()
    year = str(entry.get("year", "")).strip()

    if authors and year:
        return f"({authors}, {year})"

    if authors:
        return f"({authors})"

    if year:
        return f"({year})"

    return "(n.d.)"
