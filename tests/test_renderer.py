from pathlib import Path
from amelie_md.renderer import AmelieRenderer


def test_basic_render(tmp_path):
    renderer = AmelieRenderer(
        template_dir=Path("src/amelie_md/templates"),
        style_path=Path("src/amelie_md/styles/academic.css")
    )

    md = "# Título\n\nTexto simple"

    html = renderer.render_html(md)

    assert "<h1" in html
    assert "Texto simple" in html