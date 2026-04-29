from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt, RGBColor
from markdown_it import MarkdownIt
from markdown_it.token import Token

from amelie_md.styles.docx import AcademicDocxStyle


@dataclass(frozen=True)
class DocxMetadata:
    title: str | None = None
    author: str | None = None
    date: str | None = None


class DocxExporter:
    """Professional DOCX exporter for Amelie MD."""

    def __init__(
        self,
        metadata: DocxMetadata | None = None,
        style: str = "academic",
    ) -> None:
        self.metadata = metadata or DocxMetadata()
        self.style = style.lower().strip()
        self.parser = MarkdownIt("commonmark").enable("table")

    def export(self, markdown_text: str, output_path: str | Path) -> Path:
        path = Path(output_path)
        document = Document()

        self._configure_document(document)
        self._apply_style(document)

        if self._has_cover():
            self._add_cover(document)

        tokens = self.parser.parse(markdown_text)
        self._render_tokens(document, tokens)

        path.parent.mkdir(parents=True, exist_ok=True)
        document.save(path)

        return path

    def _configure_document(self, document: Document) -> None:
        section = document.sections[0]
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.9)
        section.right_margin = Inches(0.9)

        properties = document.core_properties

        if self.metadata.title:
            properties.title = self.metadata.title

        if self.metadata.author:
            properties.author = self.metadata.author

    def _apply_style(self, document: Document) -> None:
        if self.style != "academic":
            raise ValueError(f"Unsupported DOCX style: {self.style}")

        AcademicDocxStyle().apply(document)

    def _has_cover(self) -> bool:
        return bool(self.metadata.title or self.metadata.author or self.metadata.date)

    def _add_cover(self, document: Document) -> None:
        title = self.metadata.title or "Untitled Document"
        author = self.metadata.author or ""
        document_date = self.metadata.date or date.today().isoformat()

        document.add_paragraph("\n" * 5)

        title_paragraph = document.add_paragraph()
        title_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = title_paragraph.add_run(title)
        run.bold = True
        run.font.size = Pt(28)

        document.add_paragraph("\n" * 2)

        if author:
            author_paragraph = document.add_paragraph()
            author_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = author_paragraph.add_run(author)
            run.font.size = Pt(14)

        document.add_paragraph("\n")

        date_paragraph = document.add_paragraph()
        date_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = date_paragraph.add_run(document_date)
        run.font.size = Pt(12)

        document.add_page_break()

    def _render_tokens(self, document: Document, tokens: list[Token]) -> None:
        index = 0

        while index < len(tokens):
            token = tokens[index]

            if token.type == "heading_open":
                level = int(token.tag.removeprefix("h"))
                paragraph = document.add_heading(level=min(level, 3))
                self._add_inline_runs(paragraph, tokens[index + 1])
                index += 3
                continue

            if token.type == "paragraph_open":
                paragraph = document.add_paragraph(style="Normal")
                self._add_inline_runs(paragraph, tokens[index + 1])

                if not paragraph.text.strip():
                    self._remove_empty_paragraph(paragraph)

                index += 3
                continue

            if token.type == "bullet_list_open":
                index = self._render_list(document, tokens, index, ordered=False)
                continue

            if token.type == "ordered_list_open":
                index = self._render_list(document, tokens, index, ordered=True)
                continue

            if token.type == "fence":
                self._add_code_block(document, token.content)
                index += 1
                continue

            if token.type == "table_open":
                index = self._render_table(document, tokens, index)
                continue

            index += 1

    def _render_list(
        self,
        document: Document,
        tokens: list[Token],
        start_index: int,
        ordered: bool,
    ) -> int:
        style = "List Number" if ordered else "List Bullet"
        index = start_index + 1

        while index < len(tokens):
            token = tokens[index]

            if token.type in {"bullet_list_close", "ordered_list_close"}:
                return index + 1

            if token.type == "paragraph_open":
                paragraph = document.add_paragraph(style=style)
                self._add_inline_runs(paragraph, tokens[index + 1])

                if not paragraph.text.strip():
                    self._remove_empty_paragraph(paragraph)

                index += 3
                continue

            index += 1

        return index

    def _render_table(
        self,
        document: Document,
        tokens: list[Token],
        start_index: int,
    ) -> int:
        rows: list[list[str]] = []
        current_row: list[str] = []
        index = start_index + 1

        while index < len(tokens):
            token = tokens[index]

            if token.type == "table_close":
                break

            if token.type == "tr_open":
                current_row = []

            elif token.type in {"th_open", "td_open"}:
                current_row.append(self._inline_text(tokens[index + 1]))

            elif token.type == "tr_close":
                rows.append(current_row)

            index += 1

        if rows:
            column_count = max(len(row) for row in rows)
            table = document.add_table(rows=len(rows), cols=column_count)
            table.style = "Table Grid"

            for row_index, row in enumerate(rows):
                for column_index, value in enumerate(row):
                    cell = table.cell(row_index, column_index)
                    cell.text = value

                    if row_index == 0:
                        for paragraph in cell.paragraphs:
                            for run in paragraph.runs:
                                run.bold = True

            document.add_paragraph()

        return index + 1

    def _add_code_block(self, document: Document, code: str) -> None:
        lines = code.rstrip("\n").splitlines() or [""]

        for line in lines:
            document.add_paragraph(line, style="Amelie Code Block")

    def _inline_text(self, token: Token) -> str:
        if token.type != "inline":
            return token.content.strip()

        parts: list[str] = []

        for child in token.children or []:
            if child.type in {"text", "code_inline"}:
                parts.append(child.content)
            elif child.type in {"softbreak", "hardbreak"}:
                parts.append("\n")

        return "".join(parts).strip()

    def _add_inline_runs(self, paragraph: Any, token: Token) -> None:
        if token.type != "inline":
            if token.content:
                paragraph.add_run(token.content)
            return

        bold = False
        italic = False

        for child in token.children or []:
            if child.type == "text":
                run = paragraph.add_run(child.content)
                run.bold = bold
                run.italic = italic

            elif child.type == "strong_open":
                bold = True

            elif child.type == "strong_close":
                bold = False

            elif child.type == "em_open":
                italic = True

            elif child.type == "em_close":
                italic = False

            elif child.type == "code_inline":
                run = paragraph.add_run(child.content)
                run.bold = bold
                run.italic = italic
                run.font.name = "Consolas"
                run.font.size = Pt(9)
                run.font.color.rgb = RGBColor(45, 45, 45)

            elif child.type in {"softbreak", "hardbreak"}:
                paragraph.add_run().add_break()

    def _remove_empty_paragraph(self, paragraph: Any) -> None:
        element = paragraph._element
        element.getparent().remove(element)