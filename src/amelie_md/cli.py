from pathlib import Path

import typer

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
    to: str = typer.Option("html", help="Output format"),
    output: str | None = typer.Option(None, help="Output file"),
) -> None:
    """
    Build a technical document from Markdown into a target format.
    """

    input_path = Path(input_file)

    if not input_path.exists():
        typer.echo("❌ Input file not found")
        raise typer.Exit(code=1)

    if to != "html":
        typer.echo("❌ Only HTML supported in MVP")
        raise typer.Exit(code=1)

    output_path = Path(output) if output else input_path.with_suffix(".html")

    base_dir = Path(__file__).parent

    renderer = AmelieRenderer(
        template_dir=base_dir / "templates",
        style_path=base_dir / "styles" / "academic.css",
    )

    renderer.render_file(input_path, output_path)

    typer.echo(f"✅ Built: {output_path}")


if __name__ == "__main__":
    app()