from amelie_md.core.semantic_normalizer import (
    normalize_semantic_blocks,
    parse_admonition_marker,
)


def test_parse_admonition_marker_with_kind_only():
    kind, title, identifier = parse_admonition_marker("warning")

    assert kind == "warning"
    assert title == "Warning"
    assert identifier == ""


def test_parse_admonition_marker_with_custom_title():
    kind, title, identifier = parse_admonition_marker("note Nota técnica")

    assert kind == "note"
    assert title == "Nota técnica"
    assert identifier == ""


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
            "id": "",
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


def test_normalize_definition_block():
    blocks = [
        {"type": "paragraph", "text": ":::definition Concepto clave"},
        {"type": "paragraph", "text": "A precise academic explanation."},
        {"type": "paragraph", "text": ":::"},
    ]

    normalized = normalize_semantic_blocks(blocks)

    assert normalized == [
        {
            "type": "definition",
            "kind": "definition",
            "id": "",
            "title": "Concepto clave",
            "text": "A precise academic explanation.",
        }
    ]


def test_normalize_quote_block():
    blocks = [
        {"type": "paragraph", "text": ":::quote Autor"},
        {"type": "paragraph", "text": "Knowledge is structured meaning."},
        {"type": "paragraph", "text": ":::"},
    ]

    normalized = normalize_semantic_blocks(blocks)

    assert normalized == [
        {
            "type": "quote",
            "kind": "quote",
            "id": "",
            "title": "Autor",
            "text": "Knowledge is structured meaning.",
        }
    ]


def test_normalize_figure_block():
    blocks = [
        {"type": "paragraph", "text": ":::figure Figura 1. Arquitectura general"},
        {"type": "paragraph", "text": "Descripción visual de la arquitectura."},
        {"type": "paragraph", "text": ":::"},
    ]

    normalized = normalize_semantic_blocks(blocks)

    assert normalized == [
        {
            "type": "figure",
            "kind": "figure",
            "id": "",
            "title": "Figura 1. Arquitectura general",
            "text": "Descripción visual de la arquitectura.",
        }
    ]


def test_parse_definition_marker_with_id_and_title():
    kind, title, identifier = parse_admonition_marker(
        "definition semantic-block Semantic Block"
    )

    assert kind == "definition"
    assert identifier == "semantic-block"
    assert title == "Semantic Block"


def test_normalize_definition_with_id():
    blocks = [
        {"type": "paragraph", "text": ":::definition semantic-block Semantic Block"},
        {"type": "paragraph", "text": "Contenido semántico."},
        {"type": "paragraph", "text": ":::"},
    ]

    normalized = normalize_semantic_blocks(blocks)

    assert normalized == [
        {
            "type": "definition",
            "kind": "definition",
            "id": "semantic-block",
            "title": "Semantic Block",
            "text": "Contenido semántico.",
        }
    ]
