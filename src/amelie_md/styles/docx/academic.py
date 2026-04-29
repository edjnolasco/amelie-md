from __future__ import annotations

from docx import Document
from docx.enum.style import WD_STYLE_TYPE
from docx.shared import Inches, Pt, RGBColor


class AcademicDocxStyle:
    """Academic Word style configuration for Amelie DOCX exports."""

    code_block_style_name = "Amelie Code Block"

    def apply(self, document: Document) -> None:
        self._configure_normal(document)
        self._configure_headings(document)
        self._configure_lists(document)
        self._configure_code_block(document)

    def _configure_normal(self, document: Document) -> None:
        style = document.styles["Normal"]
        style.font.name = "Calibri"
        style.font.size = Pt(11)
        style.paragraph_format.space_before = Pt(0)
        style.paragraph_format.space_after = Pt(8)
        style.paragraph_format.line_spacing = 1.2

    def _configure_headings(self, document: Document) -> None:
        heading_specs = {
            "Heading 1": (20, RGBColor(0, 51, 102), 24, 12),
            "Heading 2": (16, RGBColor(31, 78, 121), 18, 8),
            "Heading 3": (13, RGBColor(79, 129, 189), 12, 6),
        }

        for style_name, (size, color, before, after) in heading_specs.items():
            style = document.styles[style_name]
            style.font.name = "Calibri"
            style.font.size = Pt(size)
            style.font.bold = True
            style.font.color.rgb = color
            style.paragraph_format.space_before = Pt(before)
            style.paragraph_format.space_after = Pt(after)
            style.paragraph_format.keep_with_next = True

    def _configure_lists(self, document: Document) -> None:
        for style_name in ("List Bullet", "List Number"):
            style = document.styles[style_name]
            style.font.name = "Calibri"
            style.font.size = Pt(11)
            style.paragraph_format.space_after = Pt(3)

    def _configure_code_block(self, document: Document) -> None:
        styles = document.styles

        if self.code_block_style_name in styles:
            style = styles[self.code_block_style_name]
        else:
            style = styles.add_style(
                self.code_block_style_name,
                WD_STYLE_TYPE.PARAGRAPH,
            )

        style.font.name = "Consolas"
        style.font.size = Pt(9)
        style.font.color.rgb = RGBColor(45, 45, 45)
        style.paragraph_format.left_indent = Inches(0.3)
        style.paragraph_format.right_indent = Inches(0.25)
        style.paragraph_format.space_before = Pt(8)
        style.paragraph_format.space_after = Pt(8)
        style.paragraph_format.keep_together = True