# src/amelie_md/renderers/components/html_blocks.py

from __future__ import annotations

from collections.abc import Callable
from html import escape
from typing import Any

from amelie_md.core.inline import InlineRun


InlineRenderer = Callable[[str], str]


def render_inline_html(runs: list[InlineRun]) -> str:
    parts: list[str] = []

    for run in runs:
        text = escape(run.text)

        if run.code:
            text = f"<code>{text}</code>"

        if run.bold:
            text = f"<strong>{text}</strong>"

        if run.italic:
            text = f"<em>{text}</em>"

        if run.link:
            text = f'<a href="{escape(run.link, quote=True)}">{text}</a>'

        parts.append(text)

    return "".join(parts)


def render_paragraph(
    block: dict[str, Any],
    render_inline: InlineRenderer | None = None,
) -> str:
    raw_text = str(block.get("text", "")).strip()

    if not raw_text:
        return ""

    content = render_inline(raw_text) if render_inline else escape(raw_text)
    return f"<p>{content}</p>"
