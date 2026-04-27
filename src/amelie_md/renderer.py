from pathlib import Path
from markdown import Markdown
from jinja2 import Environment, FileSystemLoader, select_autoescape


class AmelieRenderer:
    def __init__(self, template_dir: Path, style_path: Path):
        self.template_dir = template_dir
        self.style_path = style_path

        self.md = Markdown(
            extensions=[
                "extra",        # tablas, listas, etc.
                "codehilite",   # syntax highlighting
                "toc",          # tabla de contenido
                "fenced_code",
                "tables"
            ]
        )

        self.env = Environment(
            loader=FileSystemLoader(self.template_dir),
            autoescape=select_autoescape(["html"])
        )

    def render_markdown(self, markdown_text: str) -> str:
        return self.md.convert(markdown_text)

    def render_html(self, markdown_text: str) -> str:
        html_body = self.render_markdown(markdown_text)

        template = self.env.get_template("base.html")

        css = Path(self.style_path).read_text(encoding="utf-8")

        return template.render(
            content=html_body,
            style=css
        )

    def render_file(self, input_path: Path, output_path: Path):
        markdown_text = input_path.read_text(encoding="utf-8")

        html = self.render_html(markdown_text)

        output_path.write_text(html, encoding="utf-8")