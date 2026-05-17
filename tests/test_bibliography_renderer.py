from amelie_md.citations.bibliography_renderer import (
    format_bibliography_entry,
    render_bibliography_html,
)


def test_format_bibliography_entry():
    entry = {
        "authors": "Vaswani et al.",
        "year": "2017",
        "title": "Attention Is All You Need",
    }

    assert (
        format_bibliography_entry(entry)
        == "Vaswani et al. (2017). Attention Is All You Need"
    )


def test_render_bibliography_html():
    html = render_bibliography_html(
        {
            "vaswani2017": {
                "authors": "Vaswani et al.",
                "year": "2017",
                "title": "Attention Is All You Need",
            }
        }
    )

    assert "semantic-bibliography" in html
    assert 'id="ref-vaswani2017"' in html
    assert "Attention Is All You Need" in html
