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

def test_render_document_with_admonition(tmp_path):
    renderer = AmelieRenderer(
        template_dir=Path("src/amelie_md/templates"),
        style_path=Path("src/amelie_md/styles/academic.css"),
    )

    document = type(
        "Doc",
        (),
        {
            "blocks": [
                {
                    "type": "admonition",
                    "kind": "note",
                    "title": "Note",
                    "text": "Semantic blocks are supported.",
                }
            ]
        },
    )()

    html = renderer.render_document_to_html_string(document)

    assert "amelie-admonition-note" in html
    assert "Semantic blocks are supported." in html


def test_render_document_parses_admonition_markers(tmp_path):
    renderer = AmelieRenderer(
        template_dir=Path("src/amelie_md/templates"),
        style_path=Path("src/amelie_md/styles/academic.css"),
    )

    document = type(
        "Doc",
        (),
        {
            "blocks": [
                {"type": "paragraph", "text": ":::warning"},
                {"type": "paragraph", "text": "Use **safe** defaults."},
                {"type": "paragraph", "text": ":::"},
            ]
        },
    )()

    html = renderer.render_document_to_html_string(document)

    assert "amelie-admonition-warning" in html
    assert "Warning" in html
    assert "<strong>safe</strong>" in html


def test_render_document_resolves_semantic_references(tmp_path):
    renderer = AmelieRenderer(
        template_dir=Path("src/amelie_md/templates"),
        style_path=Path("src/amelie_md/styles/academic.css"),
    )

    document = type(
        "Doc",
        (),
        {
            "blocks": [
                {"type": "heading", "level": 1, "text": "Capítulo"},
                {
                    "type": "figure",
                    "id": "arch",
                    "title": "Arquitectura",
                    "text": "Diagrama del sistema.",
                },
                {"type": "paragraph", "text": "Ver {{ref:arch}}."},
            ]
        },
    )()

    html = renderer.render_document_to_html_string(document)

    assert "Figure 1.1" in html
    assert "Ver Figure 1.1." in html


def test_render_document_injects_list_of_figures(tmp_path):
    renderer = AmelieRenderer(
        template_dir=Path("src/amelie_md/templates"),
        style_path=Path("src/amelie_md/styles/academic.css"),
    )

    document = type(
        "Doc",
        (),
        {
            "blocks": [
                {"type": "heading", "level": 1, "text": "Capítulo"},
                {"type": "paragraph", "text": "[[LIST_OF_FIGURES]]"},
                {
                    "type": "figure",
                    "id": "arch",
                    "title": "Arquitectura",
                    "text": "Diagrama.",
                },
            ]
        },
    )()

    html = renderer.render_document_to_html_string(document)

    assert "List of Figures" in html
    assert "Figure 1.1. Arquitectura" in html
