from __future__ import annotations

from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape
from markdown import Markdown

from amelie_md.core.frontmatter import parse_frontmatter
from amelie_md.core.normalizer import normalize_headings

from amelie_md.core.metadata import infer_metadata

class AmelieRenderer:
    """
    Main renderer for Amelie MD.

    Pipeline:
    Markdown -> frontmatter extraction -> normalization -> HTML rendering
    """

    def __init__(self, template_dir: Path, style_path: Path):
        self.template_dir = template_dir
        self.style_path = style_path

        self.env = Environment(
            loader=FileSystemLoader(self.template_dir),
            autoescape=select_autoescape(["html"]),
        )

    def _create_markdown_engine(self) -> Markdown:
        return Markdown(
            extensions=[
                "extra",
                "codehilite",
                "toc",
                "fenced_code",
                "tables",
                "toc",
            ],
            extension_configs={
                "toc": {
                    "permalink": False,
                    "toc_depth": "1-2",
                }
            },
        )

    def render_html(self, markdown_text: str) -> str:
        metadata, content = parse_frontmatter(markdown_text)
        normalized_content = normalize_headings(content)

        markdown_engine = self._create_markdown_engine()
        html_body = markdown_engine.convert(normalized_content)
        toc_html = markdown_engine.toc

        template = self.env.get_template("base.html")
        css = self.style_path.read_text(encoding="utf-8")

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

    def _normalize_metadata(self, metadata: dict[str, Any]) -> dict[str, Any]:
        return {
            "title": metadata.get("title") or "Documento Amelie",
            "author": metadata.get("author") or "",
            "date": metadata.get("date") or "",
            "subtitle": metadata.get("subtitle") or "",
        }