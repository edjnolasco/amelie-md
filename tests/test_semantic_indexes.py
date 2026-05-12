from amelie_md.core.semantic_indexes import (
    build_semantic_index,
    inject_semantic_indexes,
)


def test_build_semantic_index_for_figures():
    blocks = [
        {"type": "figure", "id": "arch", "label": "Figure 1.1", "title": "Arquitectura"},
        {"type": "definition", "id": "concept", "label": "Definition 1.1", "title": "Concepto"},
    ]

    index = build_semantic_index(blocks, "figure")

    assert index == [
        {
            "label": "Figure 1.1",
            "title": "Arquitectura",
            "id": "arch",
        }
    ]


def test_inject_list_of_figures():
    blocks = [
        {"type": "paragraph", "text": "[[LIST_OF_FIGURES]]"},
        {"type": "figure", "id": "arch", "label": "Figure 1.1", "title": "Arquitectura"},
    ]

    injected = inject_semantic_indexes(blocks)

    assert injected[0]["type"] == "semantic_index"
    assert injected[0]["kind"] == "figures"
    assert injected[0]["items"][0]["label"] == "Figure 1.1"


def test_inject_list_of_definitions():
    blocks = [
        {"type": "paragraph", "text": "[[LIST_OF_DEFINITIONS]]"},
        {
            "type": "definition",
            "id": "concept",
            "label": "Definition 1.1",
            "title": "Concepto",
        },
    ]

    injected = inject_semantic_indexes(blocks)

    assert injected[0]["type"] == "semantic_index"
    assert injected[0]["kind"] == "definitions"
    assert injected[0]["items"][0]["label"] == "Definition 1.1"
