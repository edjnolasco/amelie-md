from amelie_md.core.semantic_numbering import (
    apply_semantic_numbering,
    semantic_label,
)


def test_semantic_label():
    assert semantic_label("definition", 1) == "Definition 1"
    assert semantic_label("figure", 2) == "Figure 2"


def test_apply_semantic_numbering():
    blocks = [
        {"type": "definition", "title": "Concepto", "text": "Texto"},
        {"type": "figure", "title": "Arquitectura", "text": "Figura"},
        {"type": "definition", "title": "Otro", "text": "Texto"},
    ]

    numbered = apply_semantic_numbering(blocks)

    assert numbered[0]["label"] == "Definition 1"
    assert numbered[1]["label"] == "Figure 1"
    assert numbered[2]["label"] == "Definition 2"
