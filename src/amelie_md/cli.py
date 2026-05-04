from __future__ import annotations

from pathlib import Path

import typer

from amelie_md.core_bridge.pipeline import process_markdown_with_core
from amelie_md.exporters.docx import DocxExporter, DocxMetadata
from amelie_md.exporters.pdf import PdfExporter
from amelie_md.renderer import AmelieRenderer
from amelie_md.document import AmelieDocument  # 🔥 NUEVO

app = typer.Typer(
    help="Amelie MD - Document normalizer and publisher",
    no_args_is_help=True,
)


@app.callback()
def main() -> None:
    """
    Amelie MD command line interface.
    """


@app.command()
def build(
    input_file: str = typer.Argument(..., help="Markdown file"),
    to: str = typer.Option("html", help="Output format: html, pdf, docx or docx-pdf"),
    output: str | None = typer.Option(None, help="Output file or output directory for docx-pdf"),
    style: str = typer.Option(
        "academic",
        help="Document style: academic | report | readme",
    ),
    title: str | None = typer.Option(None, help="DOCX cover title"),
    author: str | None = typer.Option(None, help="DOCX cover author"),
    date: str | None = typer.Option(None, help="DOCX cover date"),
    instructions: str | None = typer.Option(
        None,
        "--instructions",
        help="Style instructions in natural language",
    ),
) -> None:
    """
    Build a technical document from Markdown into a target format.
    """

    input_path = _validate_input_file(input_file)
    output_format = to.lower().strip()
    style_name = style.lower().strip()

    if output_format not in {"html", "pdf", "docx", "docx-pdf"}:
        typer.echo("❌ Supported formats: html, pdf, docx, docx-pdf")
        raise typer.Exit(code=1)

    if style_name not in {"academic", "report", "readme"}:
        typer.echo("❌ Supported styles: academic, report, readme")
        raise typer.Exit(code=1)

    markdown_text = input_path.read_text(encoding="utf-8")

    # ---------------------------
    # 🔥 NUEVO: Markdown → AmelieDocument
    # ---------------------------
    result = process_markdown_with_core(markdown_text, instructions)
    document_model = result.get("document")

    if document_model is None:
        typer.echo("❌ Failed to build document model from Markdown")
        raise typer.Exit(code=1)

    # ---------------------------
    # StyleSpec
    # ---------------------------
    style_spec = None
    style_result = result.get("style")

    if style_result and style_result.is_resolved():
        style_spec = style_result.spec
        typer.echo(f"✔ Style instructions resolved: {style_spec}")
    elif style_result and instructions:
        typer.echo("⚠️ Style ambiguity detected:")
        for ambiguity in style_result.ambiguities:
            typer.echo(f"- {ambiguity.field}: {', '.join(ambiguity.options)}")
            typer.echo(f"  {ambiguity.message}")
        raise typer.Exit(code=1)

    # ---------------------------
    # DOCX + PDF
    # ---------------------------
    if output_format == "docx-pdf":
        output_dir = Path(output) if output else input_path.parent
        output_dir.mkdir(parents=True, exist_ok=True)

        docx_output = output_dir / f"{input_path.stem}.docx"
        pdf_output = output_dir / f"{input_path.stem}.pdf"

        DocxExporter(
            metadata=DocxMetadata(
                title=title,
                author=author,
                date=date,
            ),
            style=style_name,
            style_spec=style_spec,
        ).export_document(  # 🔥 CAMBIO CLAVE
            document_model,
            docx_output,
        )

        renderer = _create_renderer(style_name)
        html = renderer.render_document_to_html_string(document_model)

        PdfExporter().export(
            html=html,
            output_path=pdf_output,
            base_url=input_path.parent,
        )

        typer.echo(f"✅ Built DOCX: {docx_output}")
        typer.echo(f"✅ Built PDF: {pdf_output}")
        typer.echo(f"ℹ️ Style: {style_name}")
        return

    # ---------------------------
    # DOCX
    # ---------------------------
    if output_format == "docx":
        output_path = Path(output) if output else input_path.with_suffix(".docx")

        DocxExporter(
            metadata=DocxMetadata(
                title=title,
                author=author,
                date=date,
            ),
            style=style_name,
            style_spec=style_spec,
        ).export_document(  # 🔥 CAMBIO CLAVE
            document_model,
            output_path,
        )

        typer.echo(f"✅ Built DOCX: {output_path}")
        typer.echo(f"ℹ️ Style: {style_name}")
        return

    # ---------------------------
    # HTML / PDF (sin cambios)
    # ---------------------------
    renderer = _create_renderer(style_name)

    if output_format == "html":
        output_path = Path(output) if output else input_path.with_suffix(".html")
        renderer.render_file(input_path, output_path)
        typer.echo(f"✅ Built HTML: {output_path}")
        typer.echo(f"ℹ️ Style: {style_name}")
        return

    output_path = Path(output) if output else input_path.with_suffix(".pdf")
    html = renderer.render_document_to_html_string(document_model)

    PdfExporter().export(
        html=html,
        output_path=output_path,
        base_url=input_path.parent,
    )

    typer.echo(f"✅ Built PDF: {output_path}")
    typer.echo(f"ℹ️ Style: {style_name}")


def _validate_input_file(input_file: str) -> Path:
    input_path = Path(input_file)

    if not input_path.exists():
        typer.echo("❌ Input file not found")
        raise typer.Exit(code=1)

    if input_path.suffix.lower() != ".md":
        typer.echo("❌ Input file must be a Markdown file (.md)")
        raise typer.Exit(code=1)

    return input_path


def _create_renderer(style_name: str = "academic") -> AmelieRenderer:
    base_dir = Path(__file__).parent
    style_path = base_dir / "styles" / f"{style_name}.css"

    if not style_path.exists():
        typer.echo(f"❌ Style not found: {style_name}")
        raise typer.Exit(code=1)

    return AmelieRenderer(
        template_dir=base_dir / "templates",
        style_path=style_path,
    )