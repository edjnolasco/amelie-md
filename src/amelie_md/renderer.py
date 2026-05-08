from __future__ import annotations

import re
from html import escape
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape
from markdown import Markdown

from amelie_md.core.frontmatter import parse_frontmatter
from amelie_md.core.metadata import infer_metadata
from amelie_md.core.normalizer import normalize_headings
from amelie_md.parsing.inline_parser import parse_inline
from amelie_md.renderers.components.html_blocks import render_paragraph


class AmelieRenderer:
    """
    Main renderer for Amelie MD.

    Legacy pipeline:
    Markdown -> normalization -> HTML

    v1.2+ pipeline:
    AmelieDocument.blocks -> HTML

    v1.3+ enhancement:
    Inline semantic rendering for paragraph, heading and list_item blocks.
    """

    def __init__(self, template_dir: Path, style_path: Path):
        self.template_dir = template_dir
        self.style_path = style_path
        self.pygments_style_path = style_path.parent / "pygments.css"
        self._heading_numbers: list[int] = []

        self.env = Environment(
            loader=FileSystemLoader(self.template_dir),
            autoescape=select_autoescape(["html"]),
        )

    def _create_markdown_engine(self) -> Markdown:
        return Markdown(
            extensions=["extra", "codehilite", "fenced_code", "tables", "toc"],
            extension_configs={
                "toc": {"permalink": False, "toc_depth": "1-2"},
                "codehilite": {
                    "guess_lang": False,
                    "use_pygments": True,
                    "noclasses": False,
                    "css_class": "codehilite",
                },
            },
        )

    def render_html(self, markdown_text: str) -> str:
        metadata, content = parse_frontmatter(markdown_text)
        normalized_content = normalize_headings(content)

        markdown_engine = self._create_markdown_engine()
        html_body = markdown_engine.convert(normalized_content)
        toc_html = markdown_engine.toc

        template = self.env.get_template("base.html")
        css = self._load_css()

        return template.render(
            metadata=infer_metadata(metadata),
            toc=toc_html,
            content=html_body,
            style=css,
        )

    def render_file(self, input_path: Path, output_path: Path) -> None:
        markdown_text = input_path.read_text(encoding="utf-8")
        html = self.render_html(markdown_text)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(html, encoding="utf-8")

    def render_to_html_string(self, input_path: Path) -> str:
        markdown_text = input_path.read_text(encoding="utf-8")
        return self.render_html(markdown_text)

    def render_document_to_html_string(self, document_model: Any) -> str:
        blocks = self._sanitize_blocks(list(getattr(document_model, "blocks", [])))

        self._heading_numbers = []
        content_html = self._render_blocks(blocks)

        self._heading_numbers = []
        toc_html = self._build_toc(blocks)

        template = self.env.get_template("base.html")
        css = self._load_css()

        metadata = {
            "title": "Documento Amelie",
            "author": "",
            "date": "",
            "subtitle": "",
        }

        return template.render(
            metadata=metadata,
            toc=toc_html,
            content=content_html,
            style=css,
        )

    def _render_blocks(self, blocks: list[dict[str, Any]]) -> str:
        html_parts: list[str] = []
        list_buffer: list[dict[str, Any]] = []
        seen_content = False

        def flush_list() -> None:
            nonlocal list_buffer, seen_content

            if not list_buffer:
                return

            rendered_list = self._render_list(list_buffer)

            if rendered_list:
                html_parts.append(rendered_list)
                seen_content = True

            list_buffer = []

        for block in blocks:
            block_type = block.get("type")

            if block_type == "list_item":
                text = str(block.get("text", "")).strip()

                if not text or not seen_content:
                    continue

                list_buffer.append(block)
                continue

            flush_list()

            if block_type == "heading":
                level = min(max(int(block.get("level", 1)), 1), 6)
                raw_text = str(block.get("text", "")).strip()

                if not raw_text:
                    continue

                rendered_text = self._render_inline_html(raw_text)
                heading_text = rendered_text
                heading_label = raw_text

                if level > 1:
                    number = self._next_heading_number(level)
                    heading_text = f"{number} {rendered_text}"
                    heading_label = f"{number} {raw_text}"

                anchor = self._slugify(heading_label)

                html_parts.append(
                    f'<h{level} id="{anchor}">{heading_text}</h{level}>'
                )
                seen_content = True

            elif block_type == "paragraph":
                paragraph_html = render_paragraph(block, self._render_inline_html)

                if paragraph_html:
                    html_parts.append(paragraph_html)
                    seen_content = True

            elif block_type == "code":
                code = str(block.get("code", "")).rstrip()

                if code:
                    html_parts.append(
                        f'<pre><code>{self._escape_html(code)}</code></pre>'
                    )
                    seen_content = True

            elif block_type == "table":
                table_html = self._render_table(block.get("rows", []))

                if table_html:
                    html_parts.append(table_html)
                    seen_content = True

            elif block_type == "toc":
                continue

        flush_list()

        return "\n".join(part for part in html_parts if part.strip())

    def _render_list(self, items: list[dict[str, Any]]) -> str:
        clean_items = [item for item in items if str(item.get("text", "")).strip()]

        if not clean_items:
            return ""

        ordered = bool(clean_items[0].get("ordered", False))
        tag = "ol" if ordered else "ul"

        parts = [f'<{tag} class="amelie-list">']

        for item in clean_items:
            raw_text = str(item.get("text", "")).strip()

            if raw_text:
                text = self._render_inline_html(raw_text)
                parts.append(f"<li>{text}</li>")

        if len(parts) == 1:
            return ""

        parts.append(f"</{tag}>")
        return "\n".join(parts)

    def _render_table(self, rows: list[list[str]]) -> str:
        rows = self._sanitize_table_rows(rows)

        if not rows:
            return ""

        html = ['<table class="amelie-table">']

        for row_index, row in enumerate(rows):
            html.append("<tr>")
            tag = "th" if row_index == 0 else "td"

            for cell in row:
                value = self._escape_html(str(cell).strip())
                html.append(f"<{tag}>{value}</{tag}>")

            html.append("</tr>")

        html.append("</table>")
        return "\n".join(html)

    def _render_inline_html(self, text: str) -> str:
        runs = parse_inline(text)
        parts: list[str] = []

        for run in runs:
            value = escape(run.text)

            if run.code:
                value = f"<code>{value}</code>"

            if run.bold:
                value = f"<strong>{value}</strong>"

            if run.italic:
                value = f"<em>{value}</em>"

            if run.link:
                value = f'<a href="{escape(run.link, quote=True)}">{value}</a>'

            parts.append(value)

        return "".join(parts)

    def _build_toc(self, blocks: list[dict[str, Any]]) -> str:
        items: list[str] = []

        for block in blocks:
            if block.get("type") != "heading":
                continue

            level = min(max(int(block.get("level", 1)), 1), 6)
            text = self._escape_html(str(block.get("text", "")).strip())

            if not text:
                continue

            label = text

            if level > 1:
                number = self._next_heading_number(level)
                label = f"{number} {text}"

            anchor = self._slugify(label)

            items.append(
                f'<li class="toc-level-{level}">'
                f'<a href="#{anchor}">{label}</a>'
                f"</li>"
            )

        if not items:
            return ""

        return '<ul class="amelie-toc">' + "".join(items) + "</ul>"

    def _next_heading_number(self, level: int) -> str:
        index = max(level - 2, 0)

        while len(self._heading_numbers) <= index:
            self._heading_numbers.append(0)

        self._heading_numbers[index] += 1
        del self._heading_numbers[index + 1 :]

        return ".".join(str(number) for number in self._heading_numbers[: index + 1]) + "."

    def _sanitize_blocks(self, blocks: list[Any]) -> list[dict[str, Any]]:
        clean_blocks: list[dict[str, Any]] = []

        for block in blocks:
            if not isinstance(block, dict):
                continue

            block_type = str(block.get("type", "")).strip()

            if not block_type:
                continue

            if block_type in {"heading", "paragraph", "list_item"}:
                text = str(block.get("text", "")).strip()

                if not text:
                    continue

                clean_block = dict(block)
                clean_block["text"] = text
                clean_blocks.append(clean_block)
                continue

            if block_type == "code":
                code = str(block.get("code", "")).rstrip()

                if not code:
                    continue

                clean_block = dict(block)
                clean_block["code"] = code
                clean_blocks.append(clean_block)
                continue

            if block_type == "table":
                rows = self._sanitize_table_rows(block.get("rows", []))

                if not rows:
                    continue

                clean_block = dict(block)
                clean_block["rows"] = rows
                clean_blocks.append(clean_block)
                continue

            if block_type == "toc":
                clean_blocks.append(dict(block))
                continue

        return clean_blocks

    def _sanitize_table_rows(self, rows: Any) -> list[list[str]]:
        if not rows:
            return []

        clean_rows: list[list[str]] = []

        for row in rows:
            if not isinstance(row, list):
                continue

            clean_row = [str(cell).strip() for cell in row]

            if any(clean_row):
                clean_rows.append(clean_row)

        return clean_rows

    def _load_css(self) -> str:
        css = self.style_path.read_text(encoding="utf-8")

        if self.pygments_style_path.exists():
            css += "\n\n" + self.pygments_style_path.read_text(encoding="utf-8")

        return css

    def _escape_html(self, text: str) -> str:
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )

    def _slugify(self, text: str) -> str:
        slug = text.lower().strip()
        slug = re.sub(r"[^\w\s-]", "", slug)
        slug = re.sub(r"\s+", "-", slug)
        slug = re.sub(r"-+", "-", slug)
        return slug or "section"

    def _normalize_metadata(self, metadata: dict[str, Any]) -> dict[str, Any]:
        return {
            "title": metadata.get("title") or "Documento Amelie",
            "author": metadata.get("author") or "",
            "date": metadata.get("date") or "",
            "subtitle": metadata.get("subtitle") or "",
        }