from __future__ import annotations

from pathlib import Path

from weasyprint import HTML


class PdfExporter:
    """
    PDF exporter based on WeasyPrint.

    It receives final HTML and writes a production-ready PDF.
    """

    def export(self, html: str, output_path: Path, base_url: Path | None = None) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)

        HTML(
            string=html,
            base_url=str(base_url) if base_url else None,
        ).write_pdf(str(output_path))