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
from amelie_md.core.semantic_pipeline import prepare_semantic_blocks
from amelie_md.citations.citation_parser import apply_citations_to_blocks, collect_cited_keys
from amelie_md.citations.citation_registry import load_citation_registry
from amelie_md.citations.bibliography_renderer import render_bibliography_html
from amelie_md.parsing.inline_parser import parse_inline
from amelie_md.renderers.components.html_blocks import render_inline_html, render_heading_block, render_list, render_list_item, render_table, render_toc, render_toc_item
from amelie_md.renderers.html_registry import build_html_registry

from amelie_md.renderers.components.html_blocks import (
    render_semantic_definition,
    render_semantic_figure,
)

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
        self.citation_registry_path = Path("references.json")

        self.registry = build_html_registry(
            render_inline=self._render_inline_html,
            render_table=self._render_table,
            escape_html=self._escape_html,
        )

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
        raw_blocks = list(getattr(document_model, "blocks", []))
        prepared_blocks = prepare_semantic_blocks(
            raw_blocks,
            html_links=True,
            inject_indexes=True,
        )

        citation_registry = load_citation_registry(
            self.citation_registry_path
        )

        cited_keys = collect_cited_keys(prepared_blocks)

        cited_blocks = apply_citations_to_blocks(
            prepared_blocks,
            citation_registry,
            html_links=True,
        )

        self._current_citation_registry = citation_registry
        self._current_cited_keys = cited_keys

        blocks = self._sanitize_blocks(cited_blocks)

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
            block_text = str(block.get("text", "")).strip()

            if block_type == "paragraph" and block_text == "[[BIBLIOGRAPHY]]":
                bibliography_html = render_bibliography_html(
                    getattr(self, "_current_citation_registry", {}),
                    cited_keys=getattr(self, "_current_cited_keys", []),
                )

                if bibliography_html:
                    flush_list()
                    html_parts.append(bibliography_html)
                    seen_content = True

                continue

            if block_type == "list_item":
                text = str(block.get("text", "")).strip()

                if not text or not seen_content:
                    continue

                list_buffer.append(block)
                continue

            flush_list()

            if self.registry.has(block_type):
                renderer = self.registry.get(block_type)
                rendered = renderer(block)

                if rendered:
                    html_parts.append(rendered)
                    seen_content = True

                continue

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
                heading_html = render_heading_block(level, heading_text, anchor)

                if heading_html:
                    html_parts.append(heading_html)
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

        rendered_items: list[str] = []

        for item in clean_items:
            raw_text = str(item.get("text", "")).strip()

            item_html = render_list_item(
                raw_text,
                self._render_inline_html,
            )

            if item_html:
                rendered_items.append(item_html)

        return render_list(rendered_items, ordered)

    def _render_table(self, rows: list[list[str]]) -> str:
        rows = self._sanitize_table_rows(rows)

        return render_table, render_toc, render_toc_item(rows, self._escape_html)

    def _render_inline_html(self, text: str) -> str:
        runs = parse_inline(text)
        return render_inline_html(runs)

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
                render_toc_item(
                    level,
                    label,
                    anchor,
                )
            )

        if not items:
            return ""

        return render_toc(items)

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

            if block_type == "admonition":
                text = str(block.get("text", "")).strip()

                if not text:
                    continue

                clean_block = dict(block)
                clean_block["text"] = text
                clean_block["kind"] = str(block.get("kind", "note")).strip() or "note"
                clean_block["title"] = str(block.get("title", "")).strip()
                clean_blocks.append(clean_block)
                continue

            if block_type == "semantic_index":
                items = block.get("items", [])

                if not isinstance(items, list):
                    continue

                clean_block = dict(block)
                clean_block["kind"] = str(block.get("kind", "")).strip()
                clean_block["title"] = str(block.get("title", "")).strip()
                clean_block["items"] = items
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


def render_semantic_html_block(block):
    """
    Semantic HTML dispatcher.
    """

    semantic_type = getattr(block, "semantic_type", None)

    if semantic_type == "definition":
        return render_semantic_definition(block)

    if semantic_type == "figure":
        return render_semantic_figure(block)

    return None

