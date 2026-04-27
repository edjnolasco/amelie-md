from __future__ import annotations

from pathlib import Path

import typer

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
    to: str = typer.Option("html", help="Output format: html or pdf"),
    output: str | None = typer.Option(None, help="Output file"),
) -> None:
    """
    Build a technical document from Markdown into a target format.
    """

    input_path = Path(input_file)

    if not input_path.exists():
        typer.echo("❌ Input file not found")
        raise typer.Exit(code=1)

    if input_path.suffix.lower() != ".md":
        typer.echo("❌ Input file must be a Markdown file (.md)")
        raise typer.Exit(code=1)

    output_format = to.lower().strip()

    if output_format not in {"html", "pdf"}:
        typer.echo("❌ Supported formats: html, pdf")
        raise typer.Exit(code=1)

    base_dir = Path(__file__).parent

    renderer = AmelieRenderer(
        template_dir=base_dir / "templates",
        style_path=base_dir / "styles" / "academic.css",
    )

    if output_format == "html":
        output_path = Path(output) if output else input_path.with_suffix(".html")
        renderer.render_file(input_path, output_path)
        typer.echo(f"✅ Built HTML: {output_path}")
        return

    output_path = Path(output) if output else input_path.with_suffix(".pdf")
    html = renderer.render_to_html_string(input_path)

    PdfExporter().export(
        html=html,
        output_path=output_path,
        base_url=input_path.parent,
    )

    typer.echo(f"✅ Built PDF: {output_path}")


if __name__ == "__main__":
    app()