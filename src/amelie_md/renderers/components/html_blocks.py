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


def render_code_block(block: dict[str, Any], escape_html) -> str:
    code = str(block.get("code", "")).rstrip()

    if not code:
        return ""

    return f'<pre><code>{escape_html(code)}</code></pre>'


def render_table(
    rows: list[list[str]],
    escape_html,
) -> str:
    if not rows:
        return ""

    html = ['<table class="amelie-table">']

    for row_index, row in enumerate(rows):
        html.append("<tr>")

        tag = "th" if row_index == 0 else "td"

        for cell in row:
            value = escape_html(str(cell).strip())
            html.append(f"<{tag}>{value}</{tag}>")

        html.append("</tr>")

    html.append("</table>")

    return "\n".join(html)


def render_heading_block(
    level: int,
    heading_text: str,
    anchor: str,
) -> str:
    level = min(max(level, 1), 6)

    if not heading_text.strip():
        return ""

    return f'<h{level} id="{escape(anchor, quote=True)}">{heading_text}</h{level}>'


def render_list_item(
    text: str,
    render_inline,
) -> str:
    clean_text = text.strip()

    if not clean_text:
        return ""

    content = render_inline(clean_text)
    return f"<li>{content}</li>"


def render_list(
    items: list[str],
    ordered: bool,
) -> str:
    clean_items = [item for item in items if item.strip()]

    if not clean_items:
        return ""

    tag = "ol" if ordered else "ul"

    html = [f'<{tag} class="amelie-list">']
    html.extend(clean_items)
    html.append(f"</{tag}>")

    return "\n".join(html)


def render_toc_item(
    level: int,
    label: str,
    anchor: str,
) -> str:
    return (
        f'<li class="toc-level-{level}">'
        f'<a href="#{escape(anchor, quote=True)}">{label}</a>'
        f"</li>"
    )


def render_toc(items: list[str]) -> str:
    clean_items = [item for item in items if item.strip()]

    if not clean_items:
        return ""

    return '<ul class="amelie-toc">' + "".join(clean_items) + "</ul>"
