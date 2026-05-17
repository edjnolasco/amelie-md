from amelie_md.citations.citation_parser import (
    apply_citations_to_blocks,
    resolve_citations,
)
from amelie_md.citations.citation_registry import format_author_year


def test_format_author_year():
    entry = {
        "authors": "Vaswani et al.",
        "year": "2017",
    }

    assert format_author_year(entry) == "(Vaswani et al., 2017)"


def test_resolve_known_citation():
    registry = {
        "vaswani2017": {
            "authors": "Vaswani et al.",
            "year": "2017",
        }
    }

    text = "The transformer architecture was introduced in [@vaswani2017]."

    assert (
        resolve_citations(text, registry)
        == "The transformer architecture was introduced in (Vaswani et al., 2017)."
    )


def test_unknown_citation_is_preserved():
    assert resolve_citations("[@missing]", {}) == "[@missing]"


def test_apply_citations_to_blocks():
    blocks = [
        {
            "type": "paragraph",
            "text": "Attention models are widely used [@vaswani2017].",
        }
    ]

    registry = {
        "vaswani2017": {
            "authors": "Vaswani et al.",
            "year": "2017",
        }
    }

    resolved = apply_citations_to_blocks(blocks, registry)

    assert resolved[0]["text"] == "Attention models are widely used (Vaswani et al., 2017)."


def test_collect_cited_keys_preserves_order_and_uniqueness():
    from amelie_md.citations.citation_parser import collect_cited_keys

    blocks = [
        {"type": "paragraph", "text": "First [@a]."},
        {"type": "paragraph", "text": "Second [@b] and again [@a]."},
    ]

    assert collect_cited_keys(blocks) == ["a", "b"]


def test_resolve_citation_as_html_backlink():
    registry = {
        "vaswani2017": {
            "authors": "Vaswani et al.",
            "year": "2017",
        }
    }

    resolved = resolve_citations(
        "See [@vaswani2017].",
        registry,
        html_links=True,
    )

    assert (
        resolved
        == 'See <a class="semantic-citation" href="#ref-vaswani2017">(Vaswani et al., 2017)</a>.'
    )
