from amelie_md.core.semantic_references import (
    apply_semantic_references,
    build_reference_map,
    resolve_references,
)


def test_build_reference_map():
    blocks = [
        {"type": "figure", "id": "arch", "label": "Figure 1.1"},
        {"type": "definition", "id": "concept", "label": "Definition 1.1"},
    ]

    references = build_reference_map(blocks)

    assert references == {
        "arch": "Figure 1.1",
        "concept": "Definition 1.1",
    }


def test_resolve_references():
    text = "See {{ref:arch}} and {{ref:concept}}."

    resolved = resolve_references(
        text,
        {
            "arch": "Figure 1.1",
            "concept": "Definition 1.1",
        },
    )

    assert resolved == "See Figure 1.1 and Definition 1.1."


def test_unknown_reference_is_preserved():
    text = "See {{ref:missing}}."

    assert resolve_references(text, {}) == "See {{ref:missing}}."


def test_apply_semantic_references():
    blocks = [
        {"type": "figure", "id": "arch", "label": "Figure 1.1", "title": "Architecture"},
        {"type": "paragraph", "text": "See {{ref:arch}}."},
    ]

    resolved = apply_semantic_references(blocks)

    assert resolved[1]["text"] == "See Figure 1.1."


def test_resolve_references_as_html_links():
    text = "See {{ref:arch}}."

    resolved = resolve_references(
        text,
        {"arch": "Figure 1.1"},
        html_links=True,
    )

    assert resolved == 'See <a href="#arch">Figure 1.1</a>.'
