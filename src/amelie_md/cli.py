from __future__ import annotations

from pathlib import Path

import typer

from amelie_md.core.encoding import read_text_with_encoding_detection
from amelie_md.core.markdown_normalizer import normalize_markdown
from amelie_md.core.validator import validate_markdown
from amelie_md.exporters.docx import DocxExporter, DocxMetadata
from amelie_md.exporters.pdf import PdfExporter
from amelie_md.renderer import AmelieRenderer

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
    to: str = typer.Option("html", help="Output format: html, pdf or docx"),
    output: str | None = typer.Option(None, help="Output file"),
    style: str = typer.Option(
        "academic",
        help="Document style: academic | report | readme",
    ),
    title: str | None = typer.Option(None, help="DOCX cover title"),
    author: str | None = typer.Option(None, help="DOCX cover author"),
    date: str | None = typer.Option(None, help="DOCX cover date"),
) -> None:
    """
    Build a technical document from Markdown into a target format.
    """

    input_path = _validate_input_file(input_file)
    output_format = to.lower().strip()
    style_name = style.lower().strip()

    if output_format not in {"html", "pdf", "docx"}:
        typer.echo("❌ Supported formats: html, pdf, docx")
        raise typer.Exit(code=1)

    if style_name not in {"academic", "report", "readme"}:
        typer.echo("❌ Supported styles: academic, report, readme")
        raise typer.Exit(code=1)

    if output_format == "docx":
        output_path = Path(output) if output else input_path.with_suffix(".docx")
        markdown_text = input_path.read_text(encoding="utf-8")

        DocxExporter(
            metadata=DocxMetadata(
                title=title,
                author=author,
                date=date,
            ),
            style=style_name,
        ).export(
            markdown_text=markdown_text,
            output_path=output_path,
        )

        typer.echo(f"✅ Built DOCX: {output_path}")
        typer.echo(f"ℹ️ Style: {style_name}")
        return

    renderer = _create_renderer(style_name)

    if output_format == "html":
        output_path = Path(output) if output else input_path.with_suffix(".html")
        renderer.render_file(input_path, output_path)
        typer.echo(f"✅ Built HTML: {output_path}")
        typer.echo(f"ℹ️ Style: {style_name}")
        return

    output_path = Path(output) if output else input_path.with_suffix(".pdf")
    html = renderer.render_to_html_string(input_path)

    PdfExporter().export(
        html=html,
        output_path=output_path,
        base_url=input_path.parent,
    )

    typer.echo(f"✅ Built PDF: {output_path}")
    typer.echo(f"ℹ️ Style: {style_name}")


@app.command()
def validate(
    input_file: str = typer.Argument(..., help="Markdown file"),
    profile: str = typer.Option(
        "technical",
        help="Validation profile: technical | readme | academic",
    ),
) -> None:
    """
    Validate Markdown structure and metadata.
    """

    input_path = _validate_input_file(input_file)
    markdown_text = input_path.read_text(encoding="utf-8")

    report = validate_markdown(markdown_text, profile=profile)

    if not report.issues:
        typer.echo("✅ No validation issues found.")
        return

    for issue in report.issues:
        icon = "❌" if issue.severity == "error" else "⚠️"
        typer.echo(f"{icon} [{issue.code}] {issue.message}")

    if report.has_errors:
        raise typer.Exit(code=1)


@app.command()
def normalize(
    input_file: str = typer.Argument(..., help="Markdown file"),
    output: str | None = typer.Option(None, help="Output Markdown file"),
) -> None:
    """
    Normalize a Markdown file and write a clean Markdown output.
    """

    input_path = _validate_input_file(input_file)
    decoded = read_text_with_encoding_detection(input_path)

    normalized = normalize_markdown(
        decoded.text,
        input_path=input_path,
        repair_encoding=True,
    )

    output_path = Path(output) if output else input_path.with_name(f"{input_path.stem}_clean.md")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(normalized, encoding="utf-8")

    typer.echo(f"✅ Normalized Markdown: {output_path}")
    typer.echo(f"ℹ️ Detected input encoding: {decoded.encoding}")
    typer.echo("✔ Converted to UTF-8")


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


if __name__ == "__main__":
    app()