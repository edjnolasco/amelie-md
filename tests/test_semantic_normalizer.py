from amelie_md.core.semantic_normalizer import (
    normalize_semantic_blocks,
    parse_admonition_marker,
)


def test_parse_admonition_marker_with_kind_only():
    kind, title = parse_admonition_marker("warning")

    assert kind == "warning"
    assert title == "Warning"


def test_parse_admonition_marker_with_custom_title():
    kind, title = parse_admonition_marker("note Nota técnica")

    assert kind == "note"
    assert title == "Nota técnica"


def test_normalize_admonition_blocks():
    blocks = [
        {"type": "paragraph", "text": ":::warning"},
        {"type": "paragraph", "text": "Use safe defaults."},
        {"type": "paragraph", "text": ":::"},
    ]

    normalized = normalize_semantic_blocks(blocks)

    assert normalized == [
        {
            "type": "admonition",
            "kind": "warning",
            "title": "Warning",
            "text": "Use safe defaults.",
        }
    ]


def test_normalize_keeps_regular_blocks():
    blocks = [
        {"type": "paragraph", "text": "Normal text."},
        {"type": "heading", "level": 1, "text": "Title"},
    ]

    assert normalize_semantic_blocks(blocks) == blocks
