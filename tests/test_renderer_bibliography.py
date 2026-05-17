from pathlib import Path

from amelie_md.renderer import AmelieRenderer


def test_renderer_renders_only_cited_bibliography_entries(tmp_path):
    references = tmp_path / "references.json"
    references.write_text(
        """
{
  "unused2020": {
    "authors": "Unused Author",
    "year": "2020",
    "title": "Unused Work"
  },
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
                },
                {
                    "type": "paragraph",
                    "text": "[[BIBLIOGRAPHY]]",
                },
            ]
        },
    )()

    html = renderer.render_document_to_html_string(document)

    assert "semantic-bibliography" in html
    assert "Attention Is All You Need" in html
    assert "Unused Work" not in html


def test_renderer_skips_empty_bibliography_when_no_citations(tmp_path):
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
                    "text": "[[BIBLIOGRAPHY]]",
                },
            ]
        },
    )()

    html = renderer.render_document_to_html_string(document)

    assert '<section class="semantic-bibliography">' not in html
