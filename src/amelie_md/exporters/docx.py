from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from docx import Document
from docx.enum.section import WD_SECTION_START
from docx.enum.table import WD_ALIGN_VERTICAL
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
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

    def __init__(self, metadata: DocxMetadata | None = None, style: str = "academic") -> None:
        self.metadata = metadata or DocxMetadata()
        self.style = style.lower().strip()
        self.parser = MarkdownIt("commonmark").enable("table")
        self.heading_num_id: int | None = None

    def export(self, markdown_text: str, output_path: str | Path) -> Path:
        path = Path(output_path)
        document = Document()

        self._configure_document(document)
        self._apply_style(document)
        self.heading_num_id = self._ensure_heading_numbering(document)

        if self._has_cover():
            self._add_cover(document)
            self._configure_content_section_pagination(document)

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

        if self.metadata.title:
            document.core_properties.title = self.metadata.title
        if self.metadata.author:
            document.core_properties.author = self.metadata.author

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

        paragraph = document.add_paragraph()
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = paragraph.add_run(title)
        run.bold = True
        run.font.size = Pt(28)

        document.add_paragraph("\n" * 2)

        if author:
            paragraph = document.add_paragraph()
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = paragraph.add_run(author)
            run.font.size = Pt(14)

        document.add_paragraph("\n")

        paragraph = document.add_paragraph()
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = paragraph.add_run(document_date)
        run.font.size = Pt(12)

        document.add_section(WD_SECTION_START.NEW_PAGE)

    def _configure_content_section_pagination(self, document: Document) -> None:
        if len(document.sections) < 2:
            return

        cover_section = document.sections[0]
        content_section = document.sections[1]

        cover_section.footer.is_linked_to_previous = False
        self._clear_footer(cover_section)

        content_section.footer.is_linked_to_previous = False
        self._restart_page_numbering(content_section, start=1)
        self._add_page_number(content_section)

    def _restart_page_numbering(self, section: Any, start: int = 1) -> None:
        sect_pr = section._sectPr

        existing_pg_num_type = sect_pr.find(qn("w:pgNumType"))
        if existing_pg_num_type is not None:
            sect_pr.remove(existing_pg_num_type)

        page_number_type = OxmlElement("w:pgNumType")
        page_number_type.set(qn("w:start"), str(start))
        sect_pr.append(page_number_type)

    def _add_page_number(self, section: Any) -> None:
        footer = section.footer
        paragraph = footer.paragraphs[0]
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER

        self._clear_paragraph(paragraph)

        paragraph.add_run("Página ")
        self._add_word_field(paragraph, "PAGE")
        paragraph.add_run(" de ")
        self._add_word_field(paragraph, "NUMPAGES")
        
    def _add_word_field(self, paragraph: Any, instruction_text: str) -> None:
        run = paragraph.add_run()

        field_begin = OxmlElement("w:fldChar")
        field_begin.set(qn("w:fldCharType"), "begin")

        instruction = OxmlElement("w:instrText")
        instruction.set(qn("xml:space"), "preserve")
        instruction.text = instruction_text

        field_end = OxmlElement("w:fldChar")
        field_end.set(qn("w:fldCharType"), "end")

        run._r.append(field_begin)
        run._r.append(instruction)
        run._r.append(field_end)    

    def _clear_footer(self, section: Any) -> None:
        footer = section.footer

        for paragraph in footer.paragraphs:
            self._clear_paragraph(paragraph)

    def _clear_paragraph(self, paragraph: Any) -> None:
        for run in list(paragraph.runs):
            paragraph._element.remove(run._element)

    def _render_tokens(self, document: Document, tokens: list[Token]) -> None:
        index = 0

        while index < len(tokens):
            token = tokens[index]

            if token.type == "heading_open":
                level = min(int(token.tag.removeprefix("h")), 3)
                paragraph = document.add_heading(level=level)

                if self.heading_num_id is not None:
                    self._apply_heading_numbering(paragraph, level, self.heading_num_id)

                self._add_inline_runs(paragraph, tokens[index + 1])
                index += 3
                continue

            if token.type == "paragraph_open":
                inline = tokens[index + 1]

                if self._is_toc_token(inline):
                    self._add_toc(document)
                    index += 3
                    continue

                paragraph = document.add_paragraph(style="Normal")
                self._add_inline_runs(paragraph, inline)

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
            table.autofit = True

            for row_index, row in enumerate(rows):
                for column_index in range(column_count):
                    value = row[column_index] if column_index < len(row) else ""
                    cell = table.cell(row_index, column_index)
                    cell.text = value
                    cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER

                    self._set_cell_margins(cell)

                    for paragraph in cell.paragraphs:
                        paragraph.paragraph_format.space_before = Pt(0)
                        paragraph.paragraph_format.space_after = Pt(0)

                        if row_index == 0:
                            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                        elif self._looks_numeric(value):
                            paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                        else:
                            paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT

                        for run in paragraph.runs:
                            run.font.name = "Calibri"
                            run.font.size = Pt(10)

                            if row_index == 0:
                                run.bold = True
                                run.font.color.rgb = RGBColor(255, 255, 255)

                    if row_index == 0:
                        self._set_cell_shading(cell, "1F4E79")

            document.add_paragraph()

        return index + 1

    def _ensure_heading_numbering(self, document: Document) -> int:
        numbering = document.part.numbering_part.element

        abstract_id = str(self._next_numbering_id(numbering, "abstractNum"))
        num_id = str(self._next_numbering_id(numbering, "num"))

        abstract = OxmlElement("w:abstractNum")
        abstract.set(qn("w:abstractNumId"), abstract_id)

        multi_level_type = OxmlElement("w:multiLevelType")
        multi_level_type.set(qn("w:val"), "multilevel")
        abstract.append(multi_level_type)

        for ilvl, level_text in {
            0: "%1",
            1: "%1.%2",
            2: "%1.%2.%3",
        }.items():
            level = OxmlElement("w:lvl")
            level.set(qn("w:ilvl"), str(ilvl))

            level.append(self._xml("w:start", val="1"))
            level.append(self._xml("w:numFmt", val="decimal"))
            level.append(self._xml("w:lvlText", val=level_text))
            level.append(self._xml("w:lvlJc", val="left"))

            paragraph_properties = OxmlElement("w:pPr")
            indent = OxmlElement("w:ind")
            indent.set(qn("w:left"), str(360 * ilvl))
            indent.set(qn("w:hanging"), "0")
            paragraph_properties.append(indent)
            level.append(paragraph_properties)

            abstract.append(level)

        numbering.append(abstract)

        numbering_instance = OxmlElement("w:num")
        numbering_instance.set(qn("w:numId"), num_id)
        numbering_instance.append(self._xml("w:abstractNumId", val=abstract_id))
        numbering.append(numbering_instance)

        return int(num_id)

    def _next_numbering_id(self, root: Any, element_name: str) -> int:
        existing_ids: list[int] = []

        for element in root.findall(qn(f"w:{element_name}")):
            attribute = "w:abstractNumId" if element_name == "abstractNum" else "w:numId"
            value = element.get(qn(attribute))

            if value is not None and value.isdigit():
                existing_ids.append(int(value))

        return max(existing_ids, default=0) + 1

    def _apply_heading_numbering(self, paragraph: Any, level: int, num_id: int) -> None:
        paragraph_properties = paragraph._element.get_or_add_pPr()

        existing_numbering = paragraph_properties.find(qn("w:numPr"))
        if existing_numbering is not None:
            paragraph_properties.remove(existing_numbering)

        numbering_properties = OxmlElement("w:numPr")
        numbering_properties.append(self._xml("w:ilvl", val=str(level - 1)))
        numbering_properties.append(self._xml("w:numId", val=str(num_id)))

        paragraph_properties.append(numbering_properties)

    def _add_toc(self, document: Document) -> None:
        paragraph = document.add_paragraph()
        run = paragraph.add_run("Table of Contents")
        run.bold = True
        run.font.size = Pt(20)
        run.font.color.rgb = RGBColor(0, 51, 102)

        paragraph = document.add_paragraph()
        field_run = paragraph.add_run()

        field_run._r.append(self._xml("w:fldChar", fldCharType="begin"))

        instruction = OxmlElement("w:instrText")
        instruction.set(qn("xml:space"), "preserve")
        instruction.text = 'TOC \\o "1-3" \\h \\z \\u'
        field_run._r.append(instruction)

        field_run._r.append(self._xml("w:fldChar", fldCharType="separate"))

        placeholder = paragraph.add_run(
            "Right-click and update field to generate table of contents"
        )
        placeholder.italic = True

        end_run = paragraph.add_run()
        end_run._r.append(self._xml("w:fldChar", fldCharType="end"))

        document.add_paragraph()
        document.add_page_break()

    def _xml(self, tag: str, **attrs: str) -> Any:
        element = OxmlElement(tag)

        for key, value in attrs.items():
            element.set(qn(f"w:{key}"), value)

        return element

    def _set_cell_margins(
        self,
        cell: Any,
        top: int = 120,
        start: int = 120,
        bottom: int = 120,
        end: int = 120,
    ) -> None:
        tc = cell._tc
        tc_pr = tc.get_or_add_tcPr()
        tc_mar = tc_pr.first_child_found_in("w:tcMar")

        if tc_mar is None:
            tc_mar = OxmlElement("w:tcMar")
            tc_pr.append(tc_mar)

        for margin_name, margin_value in {
            "top": top,
            "start": start,
            "bottom": bottom,
            "end": end,
        }.items():
            node = tc_mar.find(qn(f"w:{margin_name}"))

            if node is None:
                node = OxmlElement(f"w:{margin_name}")
                tc_mar.append(node)

            node.set(qn("w:w"), str(margin_value))
            node.set(qn("w:type"), "dxa")

    def _set_cell_shading(self, cell: Any, fill: str) -> None:
        tc_pr = cell._tc.get_or_add_tcPr()
        shading = tc_pr.find(qn("w:shd"))

        if shading is None:
            shading = OxmlElement("w:shd")
            tc_pr.append(shading)

        shading.set(qn("w:fill"), fill)

    def _looks_numeric(self, value: str) -> bool:
        cleaned = value.strip().replace(",", "").replace("%", "")

        if not cleaned:
            return False

        try:
            float(cleaned)
        except ValueError:
            return False

        return True

    def _add_code_block(self, document: Document, code: str) -> None:
        lines = code.rstrip("\n").splitlines() or [""]

        for line in lines:
            document.add_paragraph(line, style="Amelie Code Block")

    def _is_toc_token(self, token: Token) -> bool:
        if token.type != "inline":
            return False

        return self._inline_text(token).strip() == "[[TOC]]"

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
