from amelie_md.core.semantic_numbering import (
    apply_semantic_numbering,
    semantic_label,
)


def test_semantic_label_without_chapter():
    assert semantic_label("definition", 1) == "Definition 1"
    assert semantic_label("figure", 2) == "Figure 2"


def test_semantic_label_with_chapter():
    assert semantic_label("definition", 1, chapter=2) == "Definition 2.1"
    assert semantic_label("figure", 3, chapter=4) == "Figure 4.3"


def test_apply_semantic_numbering_without_heading():
    blocks = [
        {"type": "definition", "title": "Concepto", "text": "Texto"},
        {"type": "figure", "title": "Arquitectura", "text": "Figura"},
        {"type": "definition", "title": "Otro", "text": "Texto"},
    ]

    numbered = apply_semantic_numbering(blocks)

    assert numbered[0]["label"] == "Definition 1"
    assert numbered[1]["label"] == "Figure 1"
    assert numbered[2]["label"] == "Definition 2"


def test_apply_semantic_numbering_with_chapters():
    blocks = [
        {"type": "heading", "level": 1, "text": "Capítulo uno"},
        {"type": "definition", "title": "Concepto", "text": "Texto"},
        {"type": "figure", "title": "Arquitectura", "text": "Figura"},
        {"type": "definition", "title": "Otro", "text": "Texto"},
        {"type": "heading", "level": 1, "text": "Capítulo dos"},
        {"type": "figure", "title": "Modelo", "text": "Figura"},
        {"type": "definition", "title": "Nuevo", "text": "Texto"},
    ]

    numbered = apply_semantic_numbering(blocks)

    assert numbered[1]["label"] == "Definition 1.1"
    assert numbered[2]["label"] == "Figure 1.1"
    assert numbered[3]["label"] == "Definition 1.2"
    assert numbered[5]["label"] == "Figure 2.1"
    assert numbered[6]["label"] == "Definition 2.1"


def test_level_two_heading_does_not_reset_chapter_counter():
    blocks = [
        {"type": "heading", "level": 1, "text": "Capítulo uno"},
        {"type": "definition", "title": "A", "text": "Texto"},
        {"type": "heading", "level": 2, "text": "Subsección"},
        {"type": "definition", "title": "B", "text": "Texto"},
    ]

    numbered = apply_semantic_numbering(blocks)

    assert numbered[1]["label"] == "Definition 1.1"
    assert numbered[3]["label"] == "Definition 1.2"
