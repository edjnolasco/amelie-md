from pathlib import Path

from amelie_md.renderer import AmelieRenderer


class DummyDocument:
    def __init__(self, blocks):
        self.blocks = blocks


def build_renderer() -> AmelieRenderer:
    return AmelieRenderer(
        template_dir=Path("src/amelie_md/templates"),
        style_path=Path("src/amelie_md/styles/academic.css"),
    )


def test_render_paragraph_inline():
    renderer = build_renderer()

    doc = DummyDocument(
        [
            {
                "type": "paragraph",
                "text": "Texto **bold** y *italic*",
            }
        ]
    )

    html = renderer.render_document_to_html_string(doc)

    assert "<strong>bold</strong>" in html
    assert "<em>italic</em>" in html


def test_render_inline_code():
    renderer = build_renderer()

    doc = DummyDocument(
        [
            {
                "type": "paragraph",
                "text": "Usar `amelie build`",
            }
        ]
    )

    html = renderer.render_document_to_html_string(doc)

    assert "<code>amelie build</code>" in html


def test_render_link():
    renderer = build_renderer()

    doc = DummyDocument(
        [
            {
                "type": "paragraph",
                "text": "[OpenAI](https://openai.com)",
            }
        ]
    )

    html = renderer.render_document_to_html_string(doc)

    assert '<a href="https://openai.com">' in html