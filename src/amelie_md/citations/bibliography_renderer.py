from __future__ import annotations

from html import escape
from typing import Any


def format_bibliography_entry(entry: dict[str, Any]) -> str:
    authors = str(entry.get("authors", "")).strip()
    year = str(entry.get("year", "")).strip()
    title = str(entry.get("title", "")).strip()

    parts = []

    if authors:
        parts.append(authors)

    if year:
        parts.append(f"({year}).")

    if title:
        parts.append(title)

    return " ".join(parts).strip() or "Untitled reference"


def render_bibliography_html(
    registry: dict[str, dict[str, Any]],
    *,
    title: str = "References",
) -> str:
    if not registry:
        return ""

    items = []

    for key in sorted(registry):
        entry = registry[key]
        formatted = format_bibliography_entry(entry)

        items.append(
            f'<li id="ref-{escape(key, quote=True)}">'
            f"{escape(formatted)}"
            "</li>"
        )

    joined = "\n".join(items)

    return f"""
<section class="semantic-bibliography">
  <h2>{escape(title)}</h2>
  <ol>
    {joined}
  </ol>
</section>
""".strip()
