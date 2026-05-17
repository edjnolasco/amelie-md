from pathlib import Path

from amelie_md.document import AmelieDocument
from amelie_md.exporters.docx import DocxExporter
from amelie_md.renderer import AmelieRenderer


def test_semantic_showcase_html_render(tmp_path):
    renderer = AmelieRenderer(
        template_dir=Path("src/amelie_md/templates"),
        style_path=Path("src/amelie_md/styles/academic.css"),
    )

    blocks = [
        {"type": "heading", "level": 1, "text": "Semantic Foundations"},
        {
            "type": "definition",
            "id": "semantic-block",
            "title": "Semantic Block",
            "text": "Bloques académicos.",
        },
        {
            "type": "figure",
            "id": "pipeline",
            "title": "Pipeline",
            "text": "Arquitectura.",
        },
        {
            "type": "paragraph",
            "text": "Ver {{ref:semantic-block}} y {{ref:pipeline}}.",
        },
        {
            "type": "paragraph",
            "text": "[[LIST_OF_FIGURES]]",
        },
        {
            "type": "paragraph",
            "text": "[[LIST_OF_DEFINITIONS]]",
        },
    ]

    document = type("Doc", (), {"blocks": blocks})()

    html = renderer.render_document_to_html_string(document)

    assert "Definition 1.1" in html
    assert "Figure 1.1" in html
    assert 'class="semantic-reference" href="#semantic-block"' in html
    assert 'href="#pipeline"' in html
    assert "List of Figures" in html
    assert "List of Definitions" in html


def test_semantic_showcase_docx_render(tmp_path):
    output_path = tmp_path / "semantic_showcase.docx"

    exporter = DocxExporter()

    document_model = AmelieDocument(
        blocks=[
            {"type": "heading", "level": 1, "text": "Semantic Foundations"},
            {
                "type": "definition",
                "id": "semantic-block",
                "title": "Semantic Block",
                "text": "Bloques académicos.",
            },
            {
                "type": "paragraph",
                "text": "Ver {{ref:semantic-block}}.",
            },
        ]
    )

    exporter.export_document(document_model, output_path)

    assert output_path.exists()
