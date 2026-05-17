from pathlib import Path

from amelie_md.renderer import AmelieRenderer


def test_renderer_resolves_citations_from_references_json(tmp_path):
    references = tmp_path / "references.json"
    references.write_text(
        """
{
  "vaswani2017": {
    "authors": "Vaswani et al.",
    "year": "2017",
    "title": "Attention Is All You Need"
  }
}
""".strip(),
        encoding="utf-8",
    )

    renderer = AmelieRenderer(
        template_dir=Path("src/amelie_md/templates"),
        style_path=Path("src/amelie_md/styles/academic.css"),
    )
    renderer.citation_registry_path = references

    document = type(
        "Doc",
        (),
        {
            "blocks": [
                {
                    "type": "paragraph",
                    "text": "Transformers were introduced in [@vaswani2017].",
                }
            ]
        },
    )()

    html = renderer.render_document_to_html_string(document)

    assert "(Vaswani et al., 2017)" in html
    assert "[@vaswani2017]" not in html


def test_renderer_preserves_unknown_citation_without_registry():
    renderer = AmelieRenderer(
        template_dir=Path("src/amelie_md/templates"),
        style_path=Path("src/amelie_md/styles/academic.css"),
    )
    renderer.citation_registry_path = Path("missing-references.json")

    document = type(
        "Doc",
        (),
        {
            "blocks": [
                {
                    "type": "paragraph",
                    "text": "Unknown citation [@missing].",
                }
            ]
        },
    )()

    html = renderer.render_document_to_html_string(document)

    assert "[@missing]" in html
